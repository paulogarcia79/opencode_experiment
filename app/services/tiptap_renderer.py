from typing import Any
from app.config import settings

def _resolve_image_url(src: str) -> str:
    """Prepend APP_BASE_URL to relative image URLs. Leave absolute URLs unchanged."""
    if not src:
        return src
    if src.startswith(('http://', 'https://')):
        return src
    if src.startswith('/'):
        base_url = settings.APP_BASE_URL.rstrip('/')
        return f"{base_url}{src}"
    return src

def render_tiptap_node_to_html(node: Any) -> str:
    """Render a single TipTap node to HTML string."""
    if not isinstance(node, dict):
        return ""
    
    node_type = node.get("type", "")
    content = node.get("content", [])
    attrs = node.get("attrs", {})
    marks = node.get("marks", [])
    text = node.get("text", "")
    
    # Text nodes
    if node_type == "text":
        html = text
        for mark in marks:
            mark_type = mark.get("type", "")
            if mark_type == "bold":
                html = f"<strong>{html}</strong>"
            elif mark_type == "italic":
                html = f"<em>{html}</em>"
            elif mark_type == "link":
                href = mark.get("attrs", {}).get("href", "#")
                html = f'<a href="{href}">{html}</a>'
        return html
    
    # Image nodes
    if node_type == "image":
        src = _resolve_image_url(attrs.get("src", ""))
        alt = attrs.get("alt", "")
        title = attrs.get("title", "")
        title_attr = f' title="{title}"' if title else ""
        
        # Email clients are picky about images. 
        # We use inline styles and explicit width/height if available.
        # Default to max-width 100% for responsiveness.
        style = 'max-width:100%;height:auto;display:block;border-radius:12px;margin:24px 0;border:1px solid rgba(255,255,255,0.1);'
        
        width = attrs.get("width", "600")
        width_attr = f' width="{width}"' if width else ""
        
        return f'<img src="{src}" alt="{alt}"{title_attr}{width_attr} style="{style}" />'
    
    # Container nodes
    children_html = "".join(render_tiptap_node_to_html(child) for child in content)
    
    if node_type == "doc":
        return children_html
    elif node_type == "paragraph":
        return f"<p>{children_html}</p>"
    elif node_type == "heading":
        level = attrs.get("level", 2)
        return f"<h{level}>{children_html}</h{level}>"
    elif node_type == "bulletList":
        return f"<ul>{children_html}</ul>"
    elif node_type == "orderedList":
        return f"<ol>{children_html}</ol>"
    elif node_type == "listItem":
        return f"<li>{children_html}</li>"
    elif node_type == "blockquote":
        return f"<blockquote>{children_html}</blockquote>"
    elif node_type == "codeBlock":
        return f"<pre><code>{children_html}</code></pre>"
    elif node_type == "hardBreak":
        return "<br>"
    else:
        return children_html

def render_tiptap_to_email_html(content: dict) -> str:
    """Render TipTap JSON document to email-safe HTML."""
    if not content or not isinstance(content, dict):
        return ""
    
    body_html = render_tiptap_node_to_html(content)
    
    # We don't wrap in a styled div here anymore, 
    # as MJML's mj-text component will handle the container and typography.
    # We just ensure any specific overrides are handled.
    return body_html
