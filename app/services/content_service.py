def extract_plain_text_from_tiptap(content: dict) -> str:
    """Recursively extract plain text from TipTap JSON document."""
    texts = []
    
    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text" and "text" in node:
                texts.append(node["text"])
            for child in node.get("content", []):
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)
    
    walk(content)
    return " ".join(texts)

def auto_generate_description(content: dict, max_length: int = 160) -> str:
    """Generate a description from the first N characters of article plain text."""
    text = extract_plain_text_from_tiptap(content).strip()
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + "..."
