import os
import mjml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.config import settings

# Base directory for templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates", "email")

def _resolve_url(src: str) -> str:
    """
    Ensure an image path is an absolute URL.
    """
    if not src or src.startswith(('http://', 'https://', 'data:')):
        return src
    
    base = settings.APP_BASE_URL.rstrip('/')
    return f"{base}/{src.lstrip('/')}"

# Initialize Jinja2 environment
def get_env(template_dir=TEMPLATE_DIR):
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml', 'mjml'])
    )

env = get_env()

def render(template_name: str, context: dict, template_dir=None) -> str:
    """
    Render an MJML template using Jinja2 and compile it to HTML.
    """
    global env
    current_env = env
    if template_dir:
        current_env = get_env(template_dir)
        
    # 1. Inject branding configuration into context
    from datetime import datetime
    full_context = {
        "site_name": settings.SITE_NAME,
        "site_logo_url": _resolve_url(settings.SITE_LOGO_URL),
        "brand_color": settings.BRAND_PRIMARY_COLOR,
        "app_base_url": settings.APP_BASE_URL,
        "current_year": datetime.now().year,
        **context
    }

    # 2. Render MJML with Jinja2
    template = current_env.get_template(template_name)
    mjml_content = template.render(**full_context)

    # 3. Compile MJML to HTML
    result = mjml.mjml2html(mjml_content)
    
    return result
