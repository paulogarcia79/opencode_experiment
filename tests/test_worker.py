import pytest
from unittest.mock import patch
from app.worker import send_confirmation_email_task

@pytest.mark.asyncio
async def test_send_confirmation_email_task():
    email = "worker-test@example.com"
    token = "test-token"
    
    with patch("app.worker.send_confirmation_email") as mock_send:
        await send_confirmation_email_task(None, email, token)
        mock_send.assert_called_once_with(email, token)
