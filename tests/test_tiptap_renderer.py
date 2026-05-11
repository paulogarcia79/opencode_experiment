import pytest
from app.services.tiptap_renderer import render_tiptap_node_to_html, render_tiptap_to_email_html, _resolve_image_url
from app.config import settings


class TestResolveImageUrl:
    def test_prepends_base_url_to_relative_path(self):
        result = _resolve_image_url("/uploads/2025/05/test.png")
        assert result == f"{settings.APP_BASE_URL}/uploads/2025/05/test.png"

    def test_leaves_http_url_unchanged(self):
        url = "https://example.com/image.png"
        result = _resolve_image_url(url)
        assert result == url

    def test_leaves_https_url_unchanged(self):
        url = "https://cdn.example.com/photo.jpg"
        result = _resolve_image_url(url)
        assert result == url

    def test_handles_empty_src(self):
        result = _resolve_image_url("")
        assert result == ""

    def test_handles_url_without_leading_slash(self):
        result = _resolve_image_url("uploads/test.png")
        assert result == "uploads/test.png"


class TestRenderImageNode:
    def test_renders_image_with_relative_url(self):
        node = {
            "type": "image",
            "attrs": {
                "src": "/uploads/2025/05/test.png",
                "alt": "Test image",
                "title": "My Photo",
            },
        }
        html = render_tiptap_node_to_html(node)
        assert f"src=\"{settings.APP_BASE_URL}/uploads/2025/05/test.png\"" in html
        assert 'alt="Test image"' in html
        assert 'title="My Photo"' in html
        assert 'max-width:100%' in html
        assert 'height:auto' in html
        assert 'display:block' in html

    def test_renders_image_with_absolute_url(self):
        node = {
            "type": "image",
            "attrs": {
                "src": "https://cdn.example.com/photo.jpg",
                "alt": "External photo",
            },
        }
        html = render_tiptap_node_to_html(node)
        assert 'src="https://cdn.example.com/photo.jpg"' in html
        assert 'alt="External photo"' in html
        assert "APP_BASE_URL" not in html  # Should not be prepended

    def test_renders_image_without_title(self):
        node = {
            "type": "image",
            "attrs": {
                "src": "/uploads/test.png",
                "alt": "No title",
            },
        }
        html = render_tiptap_node_to_html(node)
        assert "title=" not in html

    def test_renders_image_without_alt(self):
        node = {
            "type": "image",
            "attrs": {
                "src": "/uploads/test.png",
            },
        }
        html = render_tiptap_node_to_html(node)
        assert 'alt=""' in html


class TestRenderTipTapToEmailHtml:
    def test_renders_document_with_images(self):
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello world"}],
                },
                {
                    "type": "image",
                    "attrs": {
                        "src": "/uploads/2025/05/photo.png",
                        "alt": "A photo",
                    },
                },
            ],
        }
        html = render_tiptap_to_email_html(content)
        assert "Hello world" in html
        assert f"{settings.APP_BASE_URL}/uploads/2025/05/photo.png" in html
        assert 'max-width:100%' in html
        assert 'height:auto' in html
        assert 'display:block' in html

    def test_renders_mixed_relative_and_absolute_images(self):
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "image",
                    "attrs": {
                        "src": "/uploads/local.png",
                        "alt": "Local",
                    },
                },
                {
                    "type": "image",
                    "attrs": {
                        "src": "https://external.com/img.jpg",
                        "alt": "External",
                    },
                },
            ],
        }
        html = render_tiptap_to_email_html(content)
        assert f"{settings.APP_BASE_URL}/uploads/local.png" in html
        assert 'src="https://external.com/img.jpg"' in html

    def test_returns_empty_string_for_empty_content(self):
        assert render_tiptap_to_email_html({}) == ""
        assert render_tiptap_to_email_html(None) == ""
