from .production import uptime_report, open_alerts, bandwidth_report, device_health
from .tenants import populate_tenants
from .cache import get_cache, set_cache
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pdfkit
import os
import json

load_dotenv('.env')

WKHTML_PATH = os.getenv("WKHTMLTOPDF_PATH")

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"
TEMPLATE_DIR = BASE_DIR / "templates"
TEMPLATE_NAME = "report.html"
OUTPUT_DIR = BASE_DIR.parent / "output"


def gather_data(tenant_id: str, tenant_name: str):
    """
    Pulls either fresh data or cached data

    Args:
        tenant_id (str): The tenant ID
        tenant_name (str): The tenant name
    
    Return:
        data (dict): The tenant report data
    """
    cached = get_cache(tenant_name)
    if cached:
        return cached
    uptime = uptime_report(tenant_id)
    alerts = open_alerts(tenant_id)
    bandwidth = bandwidth_report(tenant_id)
    health = device_health(tenant_id)

    data = {
        "uptime": uptime,
        "alerts": alerts,
        "bandwidth": bandwidth,
        "health": health
    }

    set_cache(data, tenant_name)
    return data

def gather_tenants():
    """
    Gathers the tenant information from the tenant JSONs

    Args:
        None
    
    Returns:
        domain_id (Dict): Tenant domain mapped to tenant ID
        domain_name (Dict): Tenant domain mapped to tenant Name
    """
    domain_id_file = 'data/tenants/domain_id.json'
    if not os.path.exists(domain_id_file):
        populate_tenants()
    
    with open(domain_id_file, 'r') as f:
            domain_id = json.load(f).get('data')

    domain_name_file = 'data/tenants/domain_name.json'
    if not os.path.exists(domain_name_file):
        populate_tenants()
    
    with open(domain_name_file, 'r') as f:
            domain_name = json.load(f).get('data')
    
    return domain_id, domain_name


def generate_report(tenant_domain) -> str:
    # Jinja env (your existing structure)
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    domain_id, domain_name = gather_tenants()

    if tenant_domain not in domain_id:
        populate_tenants()    
    tenant_id = domain_id[tenant_domain]

    # gather data
    data = gather_data(tenant_id, tenant_domain)
    uptime = data['uptime']
    alerts = data['alerts']
    bandwidth = data['bandwidth']
    health = data['health']
    name = domain_name[tenant_domain]

    #get date (Month Year)
    now = datetime.now()
    month_year = now.strftime("%B %Y")

    # render HTML
    html = env.get_template(TEMPLATE_NAME).render(
        name=name,
        date=month_year,
        uptime=uptime,
        alerts=alerts,
        bandwidth=bandwidth,
        health=health,
        assets_dir=str(ASSETS_DIR)
    )

    # ensure output folder
    OUTPUT_DIR.mkdir(exist_ok=True)

    HTML_OUT = OUTPUT_DIR / f"{tenant_domain}.html"
    PDF_OUT = OUTPUT_DIR / f"{tenant_domain}.pdf"
    

    # save HTML (handy for troubleshooting)
    HTML_OUT.write_text(html, encoding="utf-8")

    # pdfkit configuration (point to wkhtmltopdf.exe)
    if not Path(WKHTML_PATH).exists():
        raise FileNotFoundError(
            f"wkhtmltopdf not found at: {WKHTML_PATH}\n"
            "Install it or update WKHTML_PATH."
        )
    cfg = pdfkit.configuration(wkhtmltopdf=WKHTML_PATH)

    # generate PDF
    options = {
        "enable-local-file-access": "",
        "page-size": "Letter",         
        "margin-top": "10mm",
        "margin-right": "18mm",
        "margin-bottom": "10mm",
        "margin-left": "18mm",
    }

    # Use from_file so relative paths in HTML resolve nicely
    pdfkit.from_file(str(HTML_OUT), str(PDF_OUT), configuration=cfg, options=options)

    return name