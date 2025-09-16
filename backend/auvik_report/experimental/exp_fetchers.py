from dotenv import load_dotenv
from typing import List, Dict
import os
import sys
import requests
from datetime import date, timedelta
from requests.auth import HTTPBasicAuth

#Adds root directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#Imports debug helper functions
from auvik_report.debugFunctions import response_csv, error_output

#imports date range function
from auvik_report.production.fetchers import format_date_range

#Load the contents from the .env file
load_dotenv('.env')

#Get the data you need to use in your code
auvik_username: str = os.getenv('AUVIK_USERNAME')
auvik_api_key: str = os.getenv('AUVIK_API_KEY')
base_url: str = os.getenv('BASE_URL')

def fetch_alert_history(tenant: str) -> List[Dict]:
    """
    Fetches alert history for a tenant over a 30 day period

    Args:
        str: id of the tenant

    Returns:
        List[Dict]: A list containing all alert history elements
    """
    date_start, date_end = format_date_range(30)
    url = f'{base_url}/alert/history/info?tenants={tenant}&filter[detectedTimeAfter]={date_start}&filter[detectedTimeBefore]={date_end}'
    all_items = []
    while url:
        response = requests.get(url, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
        response.raise_for_status()
        body = response.json()

        all_items.extend(body.get('data', []))

        links = body.get('links', {})
        url = links.get('next')
    return all_items

def fetch_single_device_info(device_id: str) -> dict:
    """
    Get device for a single device

    Args:
        device_id (str): The device ID

    Return:
        List[Dict]:The device information
    """
    url = f"{base_url}/inventory/device/info/{device_id}"
    response = requests.get(url, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
    error_output(response)
    response.raise_for_status()
    return response.json()["data"]

def fetch_device_info(tenant: str)-> List[Dict]:
    """
    Gets all device info for the specified tenant

    Args:
        str: A string containing the id of the tenant

    Return:
        List[Dict]: A list containing all the device elements
    """
    url = f'{base_url}/inventory/device/info?tenants={tenant}&page[first]=1000'
    all_items = []
    while url:
        response = requests.get(url, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
        response.raise_for_status()
        body = response.json()

        all_items.extend(body.get('data', []))

        links = body.get('links', {})
        url = links.get('next')
    return all_items

def fetch_device_info_status(tenant: str, status: str = 'online' ) -> List[Dict]:
    """
    Gets all device info for the specified tenant and filters by status: online or offline

    Args:
        str: A string containing the id of the tenant
        str: A string secifying the device status (default = online)

    Return:
        List[Dict]: A list containing all the device elements
    """
    url = f'{base_url}/inventory/device/info?filter[onlineStatus]={status}&tenants={tenant}'
    all_items = []
    while url:
        response = requests.get(url, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
        response_csv(response)
        response.raise_for_status()
        body = response.json()

        all_items.extend(body.get('data', []))

        links = body.get('links', {})
        url = links.get('next')
    return all_items

def fetch_L2_Devices(tenant: str) -> List[Dict]:
    """
    Fetches all L2 devices per tenant

    Args:
        Tenant (str): The tenant ID
    
    Return:
        List[Dict]: All L2 device elements
    """
    urls = [
        f'{base_url}/inventory/device/info?filter[deviceType]=switch&tenants={tenant}',
        f'{base_url}/inventory/device/info?filter[deviceType]=stack&tenants={tenant}',
        f'{base_url}/inventory/device/info?filter[deviceType]=bridge&tenants={tenant}',
        f'{base_url}/inventory/device/info?filter[deviceType]=l3Switch&tenants={tenant}'
    ]
    all_items = []
    for url in urls:
        url_copy = url
        while url_copy:
            response = requests.get(url_copy, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
            response.raise_for_status()
            body = response.json()

            all_items.extend(body.get('data', []))

            links = body.get('links', {})
            url_copy = links.get('next')
    return all_items

def fetch_interface_info (interface: str) -> List[Dict]:
    """
    Get interface info for a single interface

    Args:
        device_id (str): The device ID

    Return:
        List[Dict]:The interface information
    """
    url = f"{base_url}/inventory/interface/info/{interface}"
    response = requests.get(url, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
    error_output(response)
    response.raise_for_status()
    return response.json()["data"]

def fetch_interfaces_by_type(tenant: str, type: str = 'ethernet') -> List[Dict]:
    """
    Fetches all interfaces on the network by interface type

    Args:
        Tenant (str): The tenant ID
        Type (str): The interface type you want to query (Types: https://auvikapi.us1.my.auvik.com/docs#tag/Interface)
    """
    url = f'{base_url}/inventory/interface/info?filter[interfaceType]={type}&tenants={tenant}'
    all_items = []
    while url:
        response = requests.get(url, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
        response.raise_for_status()
        body = response.json()

        all_items.extend(body.get('data', []))

        links = body.get('links', {})
        url = links.get('next')
    return all_items

def fetch_network_info(tenant: str) -> List[Dict]:
    """
    Sends request to the API to get all networks

    Args:
        str: A string containing the ID of the network you want to gain info from

    Returns:
        List[Dict]: A list containing all the "data" from the networks
    """
    url = f'{base_url}/inventory/network/info?tenants={tenant}'
    all_items = []
    while url:
        response = requests.get(url, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
        response.raise_for_status()
        body = response.json()

        all_items.extend(body.get('data', []))

        links = body.get('links', {})
        url = links.get('next')
    return all_items

def generate_date_filters(days_back: int) -> dict:
    """
    Generate filter[fromDate] and filter[thruDate] query parameters
    given a number of days back from today.
    
    :param days_back: How many days before today to start the range.
    :return: A dict with 'filter[fromDate]' and 'filter[thruDate]' strings.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def fetch_billing_usage(tenant: str) -> List[Dict]:
    """
    Sends request to get billing usage for a tenant

    Args:
        tenant (str): 

    Returns:
        List[Dict]: A list containing all the "data" from the networks
    """
    # start, end = generate_date_filters(1)
    url = f'{base_url}/billing/usage/client?tenants={tenant}&filter[fromDate]=2025-09-08&filter[thruDate]=2025-09-08'
    all_items = []
    while url:
        response = requests.get(url, auth=HTTPBasicAuth(auvik_username, auvik_api_key), headers={"Accept": "application/vnd.api+json"})
        response_csv(response)
        response.raise_for_status()
        body = response.json()

        all_items.extend(body.get('data', []))

        links = body.get('links', {})
        url = links.get('next')
    return all_items