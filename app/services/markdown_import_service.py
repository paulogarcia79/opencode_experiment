"""Markdown import service for importing .md files as draft articles."""

import re
from typing import Optional
from uuid import UUID

import frontmatter
from markdown_it import MarkdownIt
from sqlmodel import Session

from app.models import Article
from app.schemas import ImportResult, ImportSuccessItem, ImportErrorItem
from app.services.article_service import create_article, generate_slug


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
            self._in_code = False

        def _flush_text(self):
            if self._current_text:
                if self._in_code:
                    self.content.append({
                        "type": "text",
                        "text": self._current_text,
                    })
                elif self._current_marks:
                    self.content.append({
                        "type": "text",
                        "text": self._current_text,
                        "marks": list(self._current_marks),
                    })
                else:
                    self.content.append({
                        "type": "text",
                        "text": self._current_text,
                    })
                self._current_text = ""

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self._flush_text()
                level = int(tag[1])
                self._stack.append({"type": "heading", "level": level, "children": []})
            elif tag == "p":
                self._flush_text()
                self._stack.append({"type": "paragraph", "children": []})
            elif tag == "strong" or tag == "b":
                self._flush_text()
                self._current_marks.append({"type": "bold"})
            elif tag == "em" or tag == "i":
                self._flush_text()
                self._current_marks.append({"type": "italic"})
            elif tag == "code" and not self._in_code:
                if self._stack and self._stack[-1]["type"] == "pre":
                    self._in_code = True
                else:
                    self._flush_text()
                    self._current_marks.append({"type": "code"})
            elif tag == "pre":
                self._flush_text()
                self._stack.append({"type": "codeBlock", "children": [], "language": None})
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
                self.content.append({"type": "hardBreak"})
            elif tag == "table":
                self._flush_text()
                self._stack.append({"type": "table", "children": []})
            elif tag == "thead":
                self._stack.append({"type": "tableHeader", "children": [], "_row": True})
            elif tag == "tbody":
                self._stack.append({"type": "tableBody", "children": []})
            elif tag == "tr":
                parent_type = self._stack[-1]["type"] if self._stack else None
                if parent_type == "tableHeader":
                    self._stack.append({"type": "tableRow", "children": [], "_header": True})
                else:
                    self._stack.append({"type": "tableRow", "children": []})
            elif tag in ("td", "th"):
                self._stack.append({"type": "tableCell", "children": []})

        def handle_endtag(self, tag):
            self._flush_text()
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self._close_block(tag[1])
            elif tag in ("strong", "b"):
                self._remove_mark("bold")
            elif tag in ("em", "i"):
                self._remove_mark("italic")
            elif tag == "code" and self._in_code:
                self._in_code = False
                self._remove_mark("code")
            elif tag == "pre":
                self._close_code_block()
            elif tag == "blockquote":
                self._close_block("blockquote")
            elif tag in ("ul", "ol"):
                self._close_block("list")
            elif tag == "li":
                self._close_block("listItem")
            elif tag == "a":
                self._remove_mark("link")
            elif tag == "table":
                self._close_block("table")
            elif tag in ("thead", "tbody"):
                self._close_block("tableSection")
            elif tag == "tr":
                self._close_block("tableRow")
            elif tag in ("td", "th"):
                self._close_block("tableCell")

        def handle_data(self, data):
            self._current_text += data

        def _remove_mark(self, mark_type):
            self._flush_text()
            for i in range(len(self._current_marks) - 1, -1, -1):
                if self._current_marks[i]["type"] == mark_type:
                    self._current_marks.pop(i)
                    break

        def _close_block(self, block_type):
            if not self._stack:
                return
            block = self._stack.pop()
            node_type = block["type"]

            if node_type == "heading":
                children = block.get("children", [])
                if not children and self._current_text:
                    children = [{"type": "text", "text": self._current_text.strip()}]
                    self._current_text = ""
                self.content.append({
                    "type": "heading",
                    "attrs": {"level": block["level"]},
                    "content": children if children else [{"type": "text", "text": ""}],
                })
            elif node_type == "paragraph":
                children = block.get("children", [])
                if not children and self._current_text:
                    children = [{"type": "text", "text": self._current_text.strip()}]
                    self._current_text = ""
                if children or self._current_text.strip():
                    self.content.append({
                        "type": "paragraph",
                        "content": children if children else [{"type": "text", "text": self._current_text.strip()}],
                    })
                    self._current_text = ""
            elif node_type == "codeBlock":
                children = block.get("children", [])
                self.content.append({
                    "type": "codeBlock",
                    "attrs": {"language": block.get("language")},
                    "content": children if children else [{"type": "text", "text": ""}],
                })
            elif node_type == "blockquote":
                children = block.get("children", [])
                self.content.append({
                    "type": "blockquote",
                    "content": children,
                })
            elif node_type == "bulletList":
                children = block.get("children", [])
                self.content.append({
                    "type": "bulletList",
                    "content": children,
                })
            elif node_type == "orderedList":
                children = block.get("children", [])
                self.content.append({
                    "type": "orderedList",
                    "content": children,
                })
            elif node_type == "listItem":
                children = block.get("children", [])
                if not children:
                    children = [{"type": "paragraph", "content": []}]
                if self._stack:
                    parent = self._stack[-1]
                    parent["children"].append({
                        "type": "listItem",
                        "content": children,
                    })
            elif node_type == "table":
                children = block.get("children", [])
                self.content.append({
                    "type": "table",
                    "content": children,
                })
            elif node_type in ("tableHeader", "tableBody", "tableRow", "tableCell", "tableSection"):
                if self._stack:
                    parent = self._stack[-1]
                    parent["children"].append(block)
            else:
                if self._stack:
                    parent = self._stack[-1]
                    parent["children"].append(block)

        def _close_code_block(self):
            if not self._stack:
                return
            block = self._stack.pop()
            children = block.get("children", [])
            self.content.append({
                "type": "codeBlock",
                "attrs": {"language": block.get("language")},
                "content": children if children else [{"type": "text", "text": ""}],
            })

        def get_result(self):
            return {"type": "doc", "content": self.content}

    converter = TipTapConverter()
    converter.feed(html)
    return converter.get_result()


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
) -> ImportResult:
    """Import multiple markdown files as draft articles.

    Args:
        session: Database session
        files: List of (filename, content_bytes) tuples

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
            article = create_article(
                session,
                title=metadata["title"],
                content=tiptap_content,
                description=metadata.get("description"),
                send_newsletter=False,
                tag_names=metadata.get("tags", []),
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
