from .production.fetchers import fetch_tenants
from pathlib import Path
from typing import List, Dict
import json

DATA_DIR = Path('data')
TENANTS_DIR = DATA_DIR / 'tenants'

def populate_tenants() -> None:
    """
    Retrieves tenant IDS, Domain, and Name to create two json files, one mapping Domain to ID and the other mapping Domain to Name

    Args:
        None

    Returns:
        None
    """
    tenant_data = fetch_tenants()

    Domain_ID = {}
    Domain_Name = {}
    for tenant in tenant_data:
        identity = tenant['id']
        domain = tenant['attributes']['domainPrefix']
        name = tenant['attributes']['displayName']
        Domain_ID[domain] = identity
        Domain_Name[domain] = name

    DATA_DIR.mkdir(exist_ok=True)

    TENANTS_DIR.mkdir(exist_ok=True)

    Domain_ID_File = f'{TENANTS_DIR}/domain_id.json'
    with open(Domain_ID_File, 'w') as f:
        json.dump({"data": Domain_ID}, f)

    Domain_Name_File = f'{TENANTS_DIR}/domain_name.json'
    with open(Domain_Name_File, 'w') as f:
        json.dump({"data": Domain_Name}, f)

def gather_tenants() -> List[Dict]:
    """
    Creates a list of tenants intended to populate the tenants on the front end

    Args:
        None
    
    Returns:
        List[Dict]: Front end information for each tenant
    """
    tenants_data = fetch_tenants()
    tenants = []
    for tenant in tenants_data:
        domain = tenant['attributes']['domainPrefix']
        name = tenant['attributes']['displayName']
        if domain != 'sebastianit': 
            tenants.append(
                {
                    "domain": domain,
                    "name": name
                }
            )
    return tenants