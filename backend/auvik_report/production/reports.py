from dotenv import load_dotenv
from typing import List, Dict
import os
import sys
from collections import defaultdict

#Adds root directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#Imports fetchers
from .fetchers import fetch_device_availability_stats, fetch_open_alerts, fetch_device_stats, fetch_interface_stats


#imports date range function
from .helpers import health_scores, bandwidth_average, max_interface_average, stats_per_device

#Load the contents from the .env file
load_dotenv('.env')

#Get the data you need to use in your code
auvik_username: str = os.getenv('AUVIK_USERNAME')
auvik_api_key: str = os.getenv('AUVIK_API_KEY')
base_url: str = os.getenv('BASE_URL')

def uptime_report(tenant: str) -> Dict:
    """
    Generates a uptime report for the tenant
    
    Args:
        Tenant (str): The tenant ID

    Return:
        Dict: Contains the device type and average
    """
    uptime = defaultdict(float)
    count = defaultdict(int)
    valid_types = {'firewall', 'router', 'switch', 'stack', 'accessPoint', 'server', 'camera', 'storage'}
    device_availability = fetch_device_availability_stats(tenant)
    for device in device_availability:
        device_type = device['relationships']['device']['data']['deviceType']
        if device_type in valid_types:
            device_type = device_type.capitalize()
            if device_type == 'Accesspoint':
                device_type = 'Access Point'
            data = device['attributes']['stats'][0]['data']
            for day in data:
                uptime[device_type] += day[1]
                count[device_type] += 1

    averages = {}
    for device in uptime:
        averages[device] = round(uptime[device]/count[device], 3)

    return averages

def open_alerts(tenant: str) -> Dict[str, int]:
    """
    Reports the number of open alerts for at each serverity level

    Args:
        tenant (str): The tenant ID

    Results:
        Dict[str, int]: The number of open alerts at each severity level
    """
    open_alerts = fetch_open_alerts(tenant)
    if len(open_alerts) == 0:
        return {
            "No Devices" : 0
        }
    else:
        counts = {
            'Emergency': 0,
            'Critical': 0,
            'Warning': 0,
            'Info': 0,
            'Paused': 0,
            'Unknown': 0
        }
        for alert in open_alerts:
            severity = alert['attributes']['severity'].capitalize()
            status = alert['attributes']['status'].capitalize()
            counts[severity] += 1
            if status == 'Paused':
                counts[status] += 1
    return counts

def bandwidth_report(tenant: str) -> List[Dict]:
    """
    Reports bandwidth utilization for the network. Included:
        -Device
        -Type
        -Receive
        -Transmit
        -Total
        -Top interface
        -Average utilization

    Args:
        Tenant (str): The tenant ID
    
    Returns:
        Dict: All report elements
    """
    report = []

    firewalls = fetch_device_stats(tenant, 'bandwidth', 'firewall')
    routers = fetch_device_stats(tenant, 'bandwidth', 'router')
    switches = fetch_device_stats(tenant, 'bandwidth', 'switch')
    stack = fetch_device_stats(tenant, 'bandwidth', 'stack')
    aps = fetch_device_stats(tenant, 'bandwidth', 'accessPoint')

    dtypes = [firewalls, routers, switches, stack, aps]

    for dtype in dtypes:
        for device in dtype:
            name = device['relationships']['device']['data']['deviceName']
            device_type =  device['relationships']['device']['data']['deviceType'].capitalize()
            if device_type == 'Accesspoint':
                device_type = 'Access Point'
            #Check to make sure device is monitored
            if len(device['attributes']['stats'][0]['data']) > 0:
                tx_avg, rx_avg, total_avg = bandwidth_average(device)
                max_name, max_avg = max_interface_average(device)
                report.append(
                    {
                        'Device': name,
                        'Type': device_type,
                        'TX': tx_avg,
                        'RX': rx_avg,
                        'Total': total_avg,
                        'Top Interface': max_name,
                        'Average Utilization': max_avg
                    }
                )

    return report

def device_health(tenant: str) -> List[Dict]:
    """
    Gets device statistics over the course of a month and quantifies the health to identify potential problem devices

    Args:
        Tenant (str): The tenant ID

    Returns:
        List[Dict]: The device utilization stats
        List[Dict]: Teh device health scores

    """
    cpu = fetch_device_stats(tenant, 'cpuUtilization')
    memory = fetch_device_stats(tenant, 'memoryUtilization')
    storage = fetch_device_stats(tenant, 'storageUtilization')
    device_stats = stats_per_device(cpu, memory, storage)
    report = health_scores(device_stats)
    return report