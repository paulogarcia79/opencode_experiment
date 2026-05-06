from typing import Any

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
    """Render TipTap JSON document to email-safe HTML with inline styles."""
    if not content or not isinstance(content, dict):
        return ""
    
    body_html = render_tiptap_node_to_html(content)
    
    # Wrap in email-safe container with inline styles
    return f"""
    <div style="font-family: Georgia, serif; line-height: 1.6; color: #1a1a1a; max-width: 600px; margin: 0 auto;">
        {body_html}
    </div>
    """
