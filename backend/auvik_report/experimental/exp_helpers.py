from auvik_report.production.fetchers import fetch_interface_stats
from .exp_fetchers import fetch_interface_info
from typing import List, Dict
import heapq

def L2_interfaces(L2: str) -> List[Dict]:
    """
    Uses L2 devices and gets a set type of interfaces (ethernet, wifi, virtual nic)

    Args:
        L2 (str): All l2 device elements
    
    Returns:
        List[Dict]: All interfaces the meet specified types
    """
    interfacesAll = []
    types = ['ethernet', 'wifi', 'virtualNic']
    for device in L2:
        deviceID = device['id']
        for type in types:
            interfaces = fetch_interface_stats(deviceID, 'packetBroadcast', type)
            interfacesAll.extend(interfaces)
    return interfacesAll

def top_ten(interfaces: List[Dict]) -> List[Dict]:
    """
    Gets the top 10 interfaces receiving the most broadcast packets on a network

    Args:
        Interfaces: The set of interfaces

    Returns:
        List[Dict]: The top 10 interfaces
    """
    top = {}
    minimum = []
    for interface in interfaces:
        stats = interface['attributes']['stats'][0]['data']
        if len(stats) > 0:
            interfaceID = interface['id']
            interfaceName = interface['relationships']['interface']['data']['interfaceName']
            parentDevice = interface['relationships']['interface']['data']['parentDevice']
            info = fetch_interface_info(interfaceID)
            negotiatedSpeed = info['attributes']['negotiatedSpeed']
            if negotiatedSpeed != '10000000000':
                total = 0
                for entry in stats:
                    if entry[2] < 1000:
                        total += entry[2]
                average = total / len(stats)
                if len(top) < 10 or average > minimum[0][0]:
                    if len(top) >= 10:
                        lowest_avg, lowest_key = heapq.heappop(minimum)
                        del top[lowest_key]
                    top[interfaceID] = {
                            'parent': parentDevice,
                            'parentType': 'None',
                            'network': 'None',
                            'interface': interfaceName,
                            'average': average
                        }
                    heapq.heappush(minimum, (average, interfaceID))
            else:
                print("Threw a big boy out!!!")
    return sorted(top.values(), key=lambda d: d['average'], reverse=True)