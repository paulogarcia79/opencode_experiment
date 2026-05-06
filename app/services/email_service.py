import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY

def send_confirmation_email(email: str, token: str) -> None:
    if not settings.RESEND_API_KEY:
        return
    confirmation_url = f"{settings.APP_BASE_URL}/confirm?token={token}"
    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": email,
        "subject": "Confirm your newsletter subscription",
        "html": f"""
        <p>Thank you for subscribing! Please confirm your email address:</p>
        <p><a href="{confirmation_url}">Confirm Subscription</a></p>
        <p>If you did not request this, you can ignore this email.</p>
        """,
    })

def send_newsletter_email(email: str, article_title: str, article_html: str, unsubscribe_token: str) -> None:
    if not settings.RESEND_API_KEY:
        return
    unsubscribe_url = f"{settings.APP_BASE_URL}/unsubscribe?token={unsubscribe_token}"
    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": email,
        "subject": article_title,
        "html": f"""
        {article_html}
        <hr>
        <p style="font-size: 12px; color: #666;">
            <a href="{unsubscribe_url}">Unsubscribe</a>
        </p>
        """,
    })
