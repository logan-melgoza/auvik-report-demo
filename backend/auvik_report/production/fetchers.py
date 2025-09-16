from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import List, Dict
import os
import sys
import requests
from requests.auth import HTTPBasicAuth

#Adds root directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#Load the contents from the .env file
load_dotenv('.env')

#Get the data you need to use in your code
auvik_username: str = os.getenv('AUVIK_USERNAME')
auvik_api_key: str = os.getenv('AUVIK_API_KEY')
base_url: str = os.getenv('BASE_URL')
main_domain_prefix: str = os.getenv('MAIN_DOMAIN_PREFIX')

###############################################################Helper Functions######################################################################
def format_date_range(start: int) -> str:
    """
    Returns correctly formatted date in UTC from 30 days ago and today

    Args:
        int: number of days back for range
    
    Returns:
        Str: A string containing the date from specified amount of days ago in UTC
        Str: A string containing the date from today in UTC
    """
    now_utc = datetime.now(timezone.utc)
    thirty_days_ago = now_utc - timedelta(days=start)
    formatted_start = thirty_days_ago.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    formatted_end = now_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    return formatted_start, formatted_end

def fetch_paginated_data(url: str) -> List[Dict]:
    """
    Generic helper for paginated Auvik API requests

    Args (str): Initial request URL

    Returns:
        List[Dict]: Combined 'data' from all pages
    """
    all_items = []
    seen_urls = set()

    while url:
        try:
            response = requests.get(
                    url, 
                    auth=HTTPBasicAuth(auvik_username, auvik_api_key), 
                    headers={"Accept": "application/vnd.api+json"},
                    timeout=30
                )
            response.raise_for_status()
            body = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f'Network/HTTP error while fetching tenants from from {url}: {e}')
        except ValueError as e:
            raise RuntimeError(f"Invalid JSON response from {url}: {e}")
        
        all_items.extend(body.get('data', []))

        links = body.get('links', {})
        next_url = links.get('next')

        if next_url and next_url in seen_urls:
            raise RuntimeError(f"Dectected circular pagination with URL: {next}")
        seen_urls.add(url)

        url = next_url

    return all_items

###############################################################Fetcher Functions######################################################################

def fetch_tenants() -> List[Dict]:
    """
    Send the request to the API to fetch tenants

    Returns:
        List[Dict]: A list containing all tenant elements
    """
    url = f"{base_url}/tenants/detail?tenantDomainPrefix={main_domain_prefix}"
    return fetch_paginated_data(url)

def fetch_open_alerts(tenant: str) -> List[Dict]:
    """
    Fetches all open alerts for a tenant

    Args:
        str: id of the tenant

    Returns:
        List[Dict]: A list containing all alert history elements
    """
    url = f'{base_url}/alert/history/info?tenants={tenant}&filter[status]=created&filter[dismissed]=false&filter[dispatched]=true'
    return fetch_paginated_data(url)

def fetch_device_stats(tenant: str, statID: str, type: str = 'None') -> List[Dict]:
    """
    Pull device stats for the specified tenant and stat ID

    Args:
        tenant (str): The tenant ID
        statID (str): ID of stats to return [bandwidth, cpuUtilization, memoryUtilization, storageUtilization, packetUnicast, packetMulticast, packetBroadcast]
        type (str): Device type

    Returns:
        List[Dict]: A list of device elements containing the stats
    """
    date_start, date_end = format_date_range(30)
    if type == 'None':
        url = f'{base_url}/stat/device/{statID}?filter[fromTime]={date_start}&filter[thruTime]={date_end}&filter[interval]=hour&tenants={tenant}'
    else:
        url = f'{base_url}/stat/device/{statID}?filter[fromTime]={date_start}&filter[thruTime]={date_end}&filter[interval]=hour&filter[deviceType]={type}&tenants={tenant}'
    return fetch_paginated_data(url)

def fetch_device_availability_stats(tenant: str) -> List[Dict]:
    """
    Pulls device availabilty stats for the tenant over a 30 day period

    Args:
        str: The tenant ID

    Returns:
        List[Dict]: A list containing all device elements
    """
    date_start, date_end = format_date_range(30)
    url = f'{base_url}/stat/deviceAvailability/uptime?filter[fromTime]={date_start}&filter[thruTime]={date_end}&filter[interval]=hour&tenants={tenant}'
    return fetch_paginated_data(url)

def fetch_interface_stats(device: str, stat: str, type: str = 'None') -> List[Dict]:
    """
    Fetch the interface stats of a specific device

    Args:
        Device (str): The id of the target "parentDevice"
        Stat (str): The stat ID being queried
        Type (str): Optional type argument to filter by interface type

    Returns:
        List[Dict]: A list containing the stat elements
    """
    date_start, date_end = format_date_range(30)
    if type == 'None':
        url = f'{base_url}/stat/interface/{stat}?filter[fromTime]={date_start}&filter[thruTime]={date_end}&filter[interval]=hour&filter[parentDevice]={device}'
    else:
        url = f'{base_url}/stat/interface/{stat}?filter[fromTime]={date_start}&filter[thruTime]={date_end}&filter[interval]=hour&filter[parentDevice]={device}&filter[interfaceType]={type}'
    return fetch_paginated_data(url)