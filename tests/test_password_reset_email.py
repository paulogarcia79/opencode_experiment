import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import send_password_reset_email


class TestSendPasswordResetEmail:
    @patch("app.services.email_service.resend")
    def test_sends_reset_email_with_correct_content(self, mock_resend):
        """Password reset email is sent with reset URL and expiry notice."""
        with patch("app.services.email_service._process_cids") as mock_cids:
            mock_cids.return_value = ("<html>reset link: /admin/reset-password?token=test-token</html>", [])

            send_password_reset_email("admin@example.com", "test-token")

            mock_resend.Emails.send.assert_called_once()
            call_args = mock_resend.Emails.send.call_args[0][0]
            assert call_args["to"] == "admin@example.com"
            assert "reset-password?token=test-token" in call_args["html"]

    @patch("app.services.email_service.resend")
    def test_does_nothing_without_api_key(self, mock_resend):
        """No email is sent when RESEND_API_KEY is not configured."""
        with patch("app.services.email_service.settings") as mock_settings:
            mock_settings.RESEND_API_KEY = None
            mock_settings.RESEND_FROM_EMAIL = "test@example.com"
            mock_settings.APP_BASE_URL = "http://localhost:5173"
            mock_settings.SITE_NAME = "Test Site"
            mock_settings.SITE_LOGO_URL = ""
            mock_settings.BRAND_PRIMARY_COLOR = "#7C3AED"
            mock_settings.UPLOAD_DIR = "uploads"

            send_password_reset_email("admin@example.com", "test-token")

            mock_resend.Emails.send.assert_not_called()
