from dotenv import load_dotenv
from typing import List, Dict
from datetime import datetime
from collections import defaultdict
import os
import sys

#Adds root directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#imports fetchers
from .exp_fetchers import fetch_device_info_status, fetch_device_info, fetch_network_info, fetch_L2_Devices, fetch_single_device_info

#import helpers
from .exp_helpers import L2_interfaces, top_ten

#Load the contents from the .env file
load_dotenv('.env')

#Get the data you need to use in your code
auvik_username: str = os.getenv('AUVIK_USERNAME')
auvik_api_key: str = os.getenv('AUVIK_API_KEY')
base_url: str = os.getenv('BASE_URL')

def filter_alert_type(alert_history: List[Dict]) -> List[Dict]:
    """
    Takes the alert history response and categorises alerts by severity

    Args:
        List[Dict]: A list containing all alert history elements

    Returns:
        Dict[str, int]: A dictionary of alerts severity and their number of occurences
    """
    counts = {
        'emergency': 0,
        'critical': 0,
        'warning': 0,
        'info': 0,
        'unknown': 0
    }
    for alert in alert_history:
        severity = alert['attributes']['severity']
        counts[severity] += 1
    return counts


def offline_devices(tenant: str) -> List[Dict]:
    """
    Takes a tenant ID, calls the device API and reports all devices with an offline status, notes device name, last seen, and network

    Args:
        str: The tenant ID

    Returns:
        List[Dict]:  A list containing all onfline devices and info
    """
    devices = fetch_device_info_status(tenant, 'offline')
    if len(devices) == 0:
        return []
    else:
        offline_devices = []
        for device in devices:
            device_name = device['attributes']['deviceName']
            last_seen = device['attributes']['lastSeenTime']
            dt = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%S.%fZ")
            readable_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            device_network = device['relationships']['networks']['data'][0]['attributes']['networkName']
            offline_devices.append(
                {
                    "deviceName" : device_name,
                    "lastSeen" : readable_date,
                    "deviceNetwork" : device_network
                }
            )
    return offline_devices

def device_invetory(tenant: str) -> Dict[str, int]:
    """
    Uses the API device response to generate a summary of all device type and number of devices of those types on the network

    Args:
        Tenant (str): The tenant ID

    Returns:
        Dict[str, str]: Counts of devices of each type
    """
    devices = fetch_device_info(tenant)
    if len(devices) == 0:
        return {
            'No Devices' : 0
        }
    else:
        inventory = defaultdict(int)
        for device in devices:
            device_type = device['attributes']['deviceType']
            inventory[device_type] += 1
    return inventory

def network_count(networks_info: List[Dict]) -> int:
    """
    Returns the number of networks a tenant has

    Args:
        List[Dict]: A list containing all the "data" from the networks

    Returns:
        int: The number of networks found
    """
    return len(networks_info)

def network_ids(tenant: str) -> List[Dict]:
    """
    Uses the network_info gained from the API to obtain IDs for each network found

    Args: 
        Tenant (str): The tenant ID

    Returns:
        List[Dict]: A list containg each network and network name
    """
    networks_info = fetch_network_info(tenant)
    network_ids = []
    for network in networks_info:
        name = network['attributes']['networkName']
        if name == "":
            name = "No Name"
        identifier = network['id']
        network_element = {
            'network_name': name,
            'network_id': identifier
        }
        network_ids.append(network_element)
    return network_ids

def top_broadcasters(tenant: str) -> List[Dict]:
    """
    Identifies the devices sending the most broadcast packets

    Args:
        Tenant (str): The tenant ID

    Returns:
        List[Dict]: The top 5 broadcasters
    """    
    L2 = fetch_L2_Devices(tenant)
    interfaces = L2_interfaces(L2)
    top10 = top_ten(interfaces)
    for port in top10:
        parentID = port['parent']
        deviceInfo = fetch_single_device_info(parentID)
        port['parent'] = deviceInfo['attributes']['deviceName']
        port['parentType'] = deviceInfo['attributes']['deviceType']
        networks =  deviceInfo['relationships']['networks']['data']
        if len(networks) > 1:
            port['network'] = 'Multiple'
        else:
            port['network'] = deviceInfo['relationships']['networks']['data'][0]['attributes']['networkName']
    return top10