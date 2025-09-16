from typing import Dict, List, Tuple
from .fetchers import fetch_interface_stats

def score_calculator(stats: Dict) -> float:
    """
    Generates the health score for a device

    Args:
        stats (Dict): The statistics for a single device

    Return:
        flaot: The health score
    """
    values = [stats.get('cpu'), stats.get('memory'), stats.get('storage')]
    if all(v is None for v in values):
        return None  # can't calculate
    return 100 - (0.35 * (stats['cpu'] or 0) + 0.4 * (stats['memory'] or 0) + 0.25 * (stats['storage'] or 0))

def health_scores(stats: Dict) -> List[Dict]:
    """
    Takes devices statistics to give a number that quantifies overall network health and adds score to dict

    Args:
        stats (Dict): Statistics per device
    
    Return:
        Dict: Mutated version of the input
    """ 
    report = []
    for device_id, device_stats in stats.items():
        score = score_calculator(device_stats)        
        if score is not None and score < 65:
            report.append({
                'name': device_stats['name'],
                'cpu': device_stats['cpu'],
                'memory': device_stats['memory'],
                'storage': device_stats['storage'],
                'health': round(score,2)
        
            }) 
    return report

def bandwidth_average(device: List) -> int:
    """
    Takes bandwidth statistics and compiles the average for the 3 target stats (Transmitted, Receive, Total)

    Args:
        Data (List): Data from the API with device bandwidth statistics

    Returns:
        tx_avg (int): Transmitted Average
        rx_avg (int): Revceived Average
        total_avg (int): Total Average
    """
    data = device['attributes']['stats'][0]['data']  # list of [ts, tx, rx, total]
    tx_total = 0
    rx_total = 0
    total_total = 0

    for entry in data:
        tx_total += entry[1]
        rx_total += entry[2]
        total_total += entry[3]

    if data:
        n = len(data)
        tx_avg = (tx_total / n) / 1000000
        rx_avg = (rx_total / n) / 1000000
        total_avg = (total_total / n) / 1000000
    else:
        tx_avg = rx_avg = total_avg = 0

    return tx_avg, rx_avg, total_avg

def max_interface_average(device: List) -> Tuple[str, int]:
    """
    Return the ID and average of the interface with the highest average

    Arg:
        Device (List): The intermediary device to get statistics

    Return:
        name (str): Name of highest usage interface
        max_avg (int): Highest usage interface average
    """
    name =  'NA'
    percent_max = 0
    device_ID = device['id']
    interfaces = fetch_interface_stats(device_ID, 'utilization')
    for interface in interfaces:
        data = interface['attributes']['stats'][0]['data']
        if len(data) > 0:
            total = 0
            for entry in data:
                percent = entry[1]
                if percent < 200:
                    total += entry[1]
            avg = total / len(data)
            if avg > percent_max:
                name = interface['relationships']['interface']['data']['interfaceName']
                percent_max = avg

    return name, percent_max

def stats_per_device(cpu: List[Dict], memory: List[Dict], storage: List[Dict]) -> Dict:
    """
    Takes the seperate device stats and aggregates them by device ID

    Args:
        cpu (List[Dict]): Device cpu utilization stats
        memory (List[Dict]): Device memory utilization stats
        storage (List[Dict]): Device storage utilization stats
    
    Returns:
        Dict: The average of each stat per device by device ID
    """
    per_device = {}
    # Pair each payload with its metric name
    for payload, metric_name in ((cpu, 'cpu'), (memory, 'memory'), (storage, 'storage')):
        for device in payload:
            deviceID = device['relationships']['device']['data']['id']
            deviceName = device['relationships']['device']['data']['deviceName']
            rows = device['attributes']['stats'][0]['data']

            avg = (sum(entry[1] for entry in rows) / len(rows)) if rows else None

            rec = per_device.setdefault(deviceID, {
                'id': deviceID,
                'name': deviceName,
                'cpu': None,
                'memory': None,
                'storage': None,
                'health': None
            })
            if avg:
                rec[metric_name] = round(avg, 2)
            else:
                rec[metric_name] = avg
    return per_device