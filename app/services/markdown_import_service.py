"""Markdown import service for importing .md files as draft articles."""

import logging
import re
from typing import Optional
from uuid import UUID

import frontmatter
import httpx
from markdown_it import MarkdownIt
from sqlmodel import Session

from app.config import settings
from app.models import Article
from app.schemas import ImportResult, ImportSuccessItem, ImportErrorItem
from app.services.article_service import create_article, generate_slug
from app.services.storage_service import storage

logger = logging.getLogger(__name__)


def _create_md() -> MarkdownIt:
    """Create a MarkdownIt instance configured for GFM."""
    md = MarkdownIt().enable("table")
    try:
        from mdit_py_plugins.front_matter import front_matter_plugin
        md = md.use(front_matter_plugin)
    except ImportError:
        pass
    return md


def _markdown_to_tiptap(markdown: str) -> dict:
    """Convert GFM Markdown to TipTap JSON."""
    md = _create_md()
    html = md.render(markdown)
    return _html_to_tiptap(html)


def _html_to_tiptap(html: str) -> dict:
    """Convert HTML string to TipTap JSON document."""
    from html.parser import HTMLParser

    class TipTapConverter(HTMLParser):
        def __init__(self):
            super().__init__()
            self.content = []
            self._stack = []
            self._current_text = ""
            self._current_marks = []
            self._in_code_block = False
            self._code_block_text = ""

        def _current_block_children(self):
            """Return the children list of the innermost block on the stack."""
            if self._stack:
                return self._stack[-1].setdefault("children", [])
            return self.content

        def _flush_text(self):
            if not self._current_text:
                return
            text = self._current_text
            self._current_text = ""

            if self._in_code_block:
                self._code_block_text += text
                return

            # Skip whitespace-only text at root level
            if not self._stack and text.strip() == "":
                return

            target = self._current_block_children()
            if self._current_marks:
                target.append({
                    "type": "text",
                    "text": text,
                    "marks": list(self._current_marks),
                })
            else:
                target.append({
                    "type": "text",
                    "text": text,
                })

        def _wrap_text_children_in_paragraphs(self, children):
            """Wrap bare text nodes in children with paragraphs (TipTap requires blocks inside list items, table cells, etc.)."""
            result = []
            current_text_nodes = []
            for child in children:
                if child.get("type") == "text":
                    stripped = child["text"].strip()
                    if stripped:
                        current_text_nodes.append({"type": "text", "text": stripped})
                else:
                    if current_text_nodes:
                        result.append({"type": "paragraph", "content": current_text_nodes})
                        current_text_nodes = []
                    result.append(child)
            if current_text_nodes:
                result.append({"type": "paragraph", "content": current_text_nodes})
            return result if result else [{"type": "paragraph", "content": []}]

        def _filter_whitespace_children(self, children):
            """Remove whitespace-only text nodes from children."""
            return [c for c in children if c.get("type") != "text" or c.get("text", "").strip()]

        def _build_node_from_block(self, block):
            """Convert a stacked block into a TipTap node."""
            node_type = block["type"]
            children = block.get("children", [])

            if node_type == "heading":
                return {
                    "type": "heading",
                    "attrs": {"level": block["level"]},
                    "content": children if children else [{"type": "text", "text": ""}],
                }
            elif node_type == "paragraph":
                if not children:
                    return None
                return {"type": "paragraph", "content": children}
            elif node_type == "codeBlock":
                code_text = block.get("_code_text", "")
                return {
                    "type": "codeBlock",
                    "attrs": {"language": block.get("language")},
                    "content": [{"type": "text", "text": code_text}] if code_text else [{"type": "text", "text": ""}],
                }
            elif node_type == "blockquote":
                children = self._filter_whitespace_children(children)
                return {"type": "blockquote", "content": children}
            elif node_type == "bulletList":
                children = self._filter_whitespace_children(children)
                return {"type": "bulletList", "content": children}
            elif node_type == "orderedList":
                children = self._filter_whitespace_children(children)
                return {"type": "orderedList", "content": children}
            elif node_type == "listItem":
                children = self._wrap_text_children_in_paragraphs(children)
                return {"type": "listItem", "content": children}
            elif node_type == "table":
                children = self._filter_whitespace_children(children)
                return {"type": "table", "content": children}
            elif node_type == "tableSection":
                # TipTap doesn't use tableHeader/tableBody wrappers.
                # Unwrap rows directly into the parent table.
                children = self._filter_whitespace_children(children)
                if self._stack:
                    parent = self._stack[-1]
                    parent.setdefault("children", []).extend(children)
                return None
            elif node_type == "tableRow":
                children = self._filter_whitespace_children(children)
                return {"type": "tableRow", "content": children}
            elif node_type == "tableCell":
                children = self._wrap_text_children_in_paragraphs(children)
                cell_type = "tableHeader" if block.get("_header") else "tableCell"
                return {"type": cell_type, "content": children}
            return None

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self._flush_text()
                level = int(tag[1])
                self._stack.append({"type": "heading", "level": level, "children": []})
            elif tag == "p":
                self._flush_text()
                self._stack.append({"type": "paragraph", "children": []})
            elif tag in ("strong", "b"):
                self._flush_text()
                self._current_marks.append({"type": "bold"})
            elif tag in ("em", "i"):
                self._flush_text()
                self._current_marks.append({"type": "italic"})
            elif tag == "code":
                if self._stack and self._stack[-1]["type"] == "codeBlock":
                    self._in_code_block = True
                else:
                    self._flush_text()
                    self._current_marks.append({"type": "code"})
            elif tag == "pre":
                self._flush_text()
                self._stack.append({"type": "codeBlock", "children": [], "_code_text": "", "language": None})
            elif tag == "blockquote":
                self._flush_text()
                self._stack.append({"type": "blockquote", "children": []})
            elif tag == "ul":
                self._flush_text()
                self._stack.append({"type": "bulletList", "children": []})
            elif tag == "ol":
                self._flush_text()
                self._stack.append({"type": "orderedList", "children": []})
            elif tag == "li":
                self._flush_text()
                self._stack.append({"type": "listItem", "children": []})
            elif tag == "a":
                self._flush_text()
                self._current_marks.append({"type": "link", "attrs": {"href": attrs_dict.get("href", "")}})
            elif tag == "br":
                self._flush_text()
                self._current_block_children().append({"type": "hardBreak"})
            elif tag == "img":
                self._flush_text()
                src = attrs_dict.get("src", "")
                alt = attrs_dict.get("alt", "")
                image_node = {"type": "image", "attrs": {"src": src, "alt": alt}}
                self._current_block_children().append(image_node)
            elif tag == "table":
                self._flush_text()
                self._stack.append({"type": "table", "children": []})
            elif tag == "thead":
                self._stack.append({"type": "tableSection", "children": [], "_header": True})
            elif tag == "tbody":
                self._stack.append({"type": "tableSection", "children": [], "_header": False})
            elif tag == "tr":
                self._stack.append({"type": "tableRow", "children": []})
            elif tag in ("td", "th"):
                self._stack.append({"type": "tableCell", "children": [], "_header": tag == "th"})

        def handle_endtag(self, tag):
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self._flush_text()
                self._close_block()
            elif tag == "p":
                self._flush_text()
                self._close_block()
            elif tag in ("strong", "b"):
                self._flush_text()
                self._remove_mark("bold")
            elif tag in ("em", "i"):
                self._flush_text()
                self._remove_mark("italic")
            elif tag == "code" and self._in_code_block:
                self._in_code_block = False
            elif tag == "code" and not self._in_code_block:
                self._flush_text()
                self._remove_mark("code")
            elif tag == "pre":
                self._flush_text()
                self._close_block()
            elif tag == "blockquote":
                self._flush_text()
                self._close_block()
            elif tag in ("ul", "ol"):
                self._flush_text()
                self._close_block()
            elif tag == "li":
                self._flush_text()
                self._close_block()
            elif tag == "a":
                self._flush_text()
                self._remove_mark("link")
            elif tag == "table":
                self._flush_text()
                self._close_block()
            elif tag in ("thead", "tbody"):
                self._flush_text()
                self._close_block()
            elif tag == "tr":
                self._flush_text()
                self._close_block()
            elif tag in ("td", "th"):
                self._flush_text()
                self._close_block()

        def handle_data(self, data):
            if self._in_code_block and self._stack:
                self._stack[-1]["_code_text"] += data
            else:
                self._current_text += data

        def _remove_mark(self, mark_type):
            for i in range(len(self._current_marks) - 1, -1, -1):
                if self._current_marks[i]["type"] == mark_type:
                    self._current_marks.pop(i)
                    break

        def _close_block(self):
            if not self._stack:
                return
            block = self._stack.pop()
            node = self._build_node_from_block(block)
            if node is None:
                return

            if self._stack:
                parent = self._stack[-1]
                parent.setdefault("children", []).append(node)
            else:
                self.content.append(node)

        def get_result(self):
            return {"type": "doc", "content": self.content}

    converter = TipTapConverter()
    converter.feed(html)
    return converter.get_result()


def _download_remote_images(tiptap_doc: dict) -> list[str]:
    """Walk TipTap JSON, download remote images, rewrite src to local paths.

    Returns list of error messages for failed downloads.
    """
    errors = []
    _walk_and_download(tiptap_doc, errors)
    return errors


def _walk_and_download(node: dict, errors: list[str]) -> None:
    """Recursively walk TipTap JSON and download remote images."""
    if node.get("type") == "image":
        attrs = node.get("attrs", {})
        src = attrs.get("src", "")
        if not src or src.startswith("/uploads/"):
            return

        try:
            response = httpx.get(src, follow_redirects=True, timeout=10.0)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if content_type not in settings.ALLOWED_IMAGE_TYPES:
                errors.append(f"Image skipped (unsupported type {content_type}): {src}")
                return

            ext = _extension_from_mime(content_type)
            filename = src.split("/")[-1].split("?")[0] or f"image{ext}"
            if not filename.endswith(ext):
                filename = f"{filename}{ext}"

            result = storage.save(
                file_bytes=response.content,
                filename=filename,
                mime_type=content_type,
            )
            attrs["src"] = result["url"]
        except httpx.HTTPStatusError as e:
            errors.append(f"Image download failed (HTTP {e.response.status_code}): {src}")
        except Exception as e:
            errors.append(f"Image download failed ({str(e)}): {src}")
        return

    if "content" in node:
        for child in node["content"]:
            _walk_and_download(child, errors)


def _extension_from_mime(mime_type: str) -> str:
    """Map MIME type to file extension."""
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
    }
    return mapping.get(mime_type, ".bin")


def _extract_frontmatter(content: str, filename: str) -> dict:
    """Parse YAML frontmatter from markdown content."""
    try:
        post = frontmatter.loads(content)
    except Exception:
        return {"title": filename.replace(".md", "").replace("-", " ").title(), "content": content, "tags": []}

    title = post.get("title") or filename.replace(".md", "").replace("-", " ").title()
    tags = post.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in re.split(r"[,;]", tags) if t.strip()]

    metadata = {
        "title": title,
        "description": post.get("description"),
        "tags": tags,
        "slug": post.get("slug"),
        "content": post.content,
    }
    return metadata


def import_markdown_files(
    session: Session,
    files: list[tuple[str, bytes]],
    author_id: Optional[uuid.UUID] = None,
) -> ImportResult:
    """Import multiple markdown files as draft articles.

    Args:
        session: Database session
        files: List of (filename, content_bytes) tuples
        author_id: Optional author ID to assign to imported articles

    Returns:
        ImportResult with successes and errors
    """
    successes = []
    errors = []

    for filename, content_bytes in files:
        try:
            content_str = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(ImportErrorItem(
                filename=filename,
                error="File is not valid UTF-8",
            ))
            continue

        try:
            metadata = _extract_frontmatter(content_str, filename)
        except Exception as e:
            errors.append(ImportErrorItem(
                filename=filename,
                error=f"Failed to parse frontmatter: {str(e)}",
            ))
            continue

        try:
            tiptap_content = _markdown_to_tiptap(metadata["content"])
        except Exception as e:
            errors.append(ImportErrorItem(
                filename=filename,
                error=f"Failed to convert markdown: {str(e)}",
            ))
            continue

        try:
            image_errors = _download_remote_images(tiptap_content)
            for err in image_errors:
                logger.warning(f"[{filename}] {err}")
                errors.append(ImportErrorItem(
                    filename=filename,
                    error=err,
                ))
        except Exception as e:
            errors.append(ImportErrorItem(
                filename=filename,
                error=f"Failed to process images: {str(e)}",
            ))

        try:
            article = create_article(
                session,
                title=metadata["title"],
                content=tiptap_content,
                description=metadata.get("description"),
                send_newsletter=False,
                tag_names=metadata.get("tags", []),
                author_id=author_id,
            )
            successes.append(ImportSuccessItem(
                id=str(article.id),
                title=article.title,
                slug=article.slug,
            ))
        except Exception as e:
            errors.append(ImportErrorItem(
                filename=filename,
                error=f"Failed to create article: {str(e)}",
            ))
            continue

    return ImportResult(
        successes=successes,
        errors=errors,
        total=len(files),
    )
