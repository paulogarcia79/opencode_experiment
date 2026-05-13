import resend
import logging
import re
import os
import mimetypes
from datetime import datetime
from app.config import settings
from app.services.email_renderer import render

resend.api_key = settings.RESEND_API_KEY

logger = logging.getLogger(__name__)

class EmailServiceError(Exception):
    """Custom exception for email service failures."""
    pass

def _process_cids(html: str):
    """
    Find all local images in HTML, convert them to CID references,
    and return the updated HTML and a list of attachments.
    """
    attachments = []
    cids = {}
    
    # Construct absolute path to upload directory
    # Get the project root (where the 'uploads' folder lives)
    current_file = os.path.abspath(__file__)
    # app/services/email_service.py -> app/services/ -> app/ -> project_root/
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    upload_dir = os.path.join(project_root, settings.UPLOAD_DIR)
    
    # Regex to find /uploads/filename.ext
    pattern = r'src="([^"]*/' + re.escape(settings.UPLOAD_DIR) + r'/([^"]+))"'
    
    def replace_with_cid(match):
        full_match = match.group(0)
        filename = match.group(2)
        
        # Unique CID for this filename (deduplicate same image referenced multiple times)
        if filename not in cids:
            file_path = os.path.join(upload_dir, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        content = list(f.read())
                        cid = f"img_{len(attachments)}"
                        cids[filename] = cid
                        attachments.append({
                            "filename": filename,
                            "content": content,
                            "content_id": cid
                        })
                        return f'src="cid:{cid}"'
                except Exception as e:
                    logger.error(f"Failed to read image for CID: {file_path}. Error: {e}")
        else:
            return f'src="cid:{cids[filename]}"'
            
        return full_match # Fallback to original if file not found

    new_html = re.sub(pattern, replace_with_cid, html)
    return new_html, attachments

def send_confirmation_email(email: str, token: str) -> None:
    if not settings.RESEND_API_KEY:
        return
    confirmation_url = f"{settings.APP_BASE_URL}/confirm?token={token}"
    
    html = render("confirmation.mjml", {
        "confirmation_url": confirmation_url,
        "preview_text": "Please confirm your subscription to our newsletter.",
    })
    
    html, attachments = _process_cids(html)
    
    try:
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": email,
            "subject": f"Confirm your subscription to {settings.SITE_NAME}",
            "html": html,
        }
        if attachments:
            params["attachments"] = attachments
            
        resend.Emails.send(params)
    except Exception as e:
        logger.error(f"Failed to send confirmation email to {email}: {str(e)}")
        raise EmailServiceError(str(e))

def send_newsletter_email(email: str, article_title: str, article_html: str, unsubscribe_token: str, send_id: str = None) -> None:
    if not settings.RESEND_API_KEY:
        return
    unsubscribe_url = f"{settings.APP_BASE_URL}/unsubscribe?token={unsubscribe_token}"
    
    html = render("newsletter.mjml", {
        "article_title": article_title,
        "article_html": article_html,
        "unsubscribe_url": unsubscribe_url,
        "preview_text": article_title,
    })
    
    html, attachments = _process_cids(html)
    
    try:
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": email,
            "subject": article_title,
            "html": html,
        }
        if attachments:
            params["attachments"] = attachments
        
        if send_id:
            params["tags"] = [{"name": "newsletter_send_id", "value": send_id}]
            
        resend.Emails.send(params)
    except Exception as e:
        logger.error(f"Failed to send newsletter email to {email}: {str(e)}")
        raise EmailServiceError(str(e))

def send_password_reset_email(email: str, reset_token: str) -> None:
    if not settings.RESEND_API_KEY:
        return
    reset_url = f"{settings.APP_BASE_URL}/admin/reset-password?token={reset_token}"
    
    html = render("password_reset.mjml", {
        "reset_url": reset_url,
        "preview_text": "Reset your password.",
    })
    
    html, attachments = _process_cids(html)
    
    try:
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": email,
            "subject": f"Reset your password for {settings.SITE_NAME}",
            "html": html,
        }
        if attachments:
            params["attachments"] = attachments
            
        resend.Emails.send(params)
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        raise EmailServiceError(str(e))

def send_verification_email(email: str, verification_token: str, role: str = "contributor") -> None:
    if not settings.RESEND_API_KEY:
        return
    verification_url = f"{settings.APP_BASE_URL}/verify-email?token={verification_token}"

    html = render("email_verification.mjml", {
        "verification_url": verification_url,
        "preview_text": "Verify your email address.",
        "role": role,
    })

    html, attachments = _process_cids(html)

    try:
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": email,
            "subject": f"Verify your email for {settings.SITE_NAME}",
            "html": html,
        }
        if attachments:
            params["attachments"] = attachments

        resend.Emails.send(params)
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        raise EmailServiceError(str(e))

def send_invite_email(email: str, setup_token: str, role: str) -> None:
    if not settings.RESEND_API_KEY:
        return
    setup_url = f"{settings.APP_BASE_URL}/auth?setup={setup_token}"

    html = render("invite.mjml", {
        "setup_url": setup_url,
        "role": role,
        "preview_text": f"You've been invited to join {settings.SITE_NAME} as a {role}.",
    })

    html, attachments = _process_cids(html)

    try:
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": email,
            "subject": f"You're invited to join {settings.SITE_NAME}",
            "html": html,
        }
        if attachments:
            params["attachments"] = attachments

        resend.Emails.send(params)
    except Exception as e:
        logger.error(f"Failed to send invite email to {email}: {str(e)}")
        raise EmailServiceError(str(e))
