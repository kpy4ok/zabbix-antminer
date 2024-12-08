#!/usr/bin/env python3
import sys
import logging
import requests
from requests.auth import HTTPDigestAuth
import json

def get_value(host, port, username, password, item):
    """
    Retrieves specific values from the miner's API
    """
    try:
        response = requests.get(
            f'http://{host}:{port}/cgi-bin/stats.cgi',
            auth=HTTPDigestAuth(username, password),
            timeout=5
        )
        data = response.json()
        
        # Parse the item path
        keys = item.split('.')
        
        # Get the stats object
        stats = data['STATS'][0]  # First element contains all stats
        
        # Handle different data paths
        if keys[0] == 'STATS':
            if len(keys) > 2:
                if keys[1] == 'chain':
                    chain_index = int(keys[2])
                    metric = keys[3]
                    
                    # Make sure chain index is valid
                    if chain_index < len(stats['chain']):
                        chain = stats['chain'][chain_index]
                        
                        # Map the metric names to their JSON counterparts
                        metric_map = {
                            'freq_avg': 'freq_avg',
                            'rate_real': 'rate_real',
                            'hw': 'hw',
                            'temp_chip': 'temp_chip',
                            'temp_pcb': 'temp_pcb',
                            'temp_pic': 'temp_pic'
                        }
                        
                        if metric in metric_map:
                            value = chain[metric_map[metric]]
                            # If it's a temperature array, return first value
                            if isinstance(value, list):
                                return value[0]
                            return value
                elif keys[1] == 'fan':
                    fan_index = int(keys[2])
                    if fan_index < len(stats['fan']):
                        return stats['fan'][fan_index]
                else:
                    # Handle other STATS metrics
                    metric = keys[1]
                    if metric in stats:
                        return stats[metric]
        
        logging.error(f"Path not found: {item}")
        return 0
        
    except Exception as e:
        logging.error(f"Error getting value: {str(e)}")
        return 0

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    
    if len(sys.argv) < 2:
        print("Usage: script <action> <host> <port> <username> <password> <item>")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "get":
        if len(sys.argv) != 7:
            print("Usage for getting values: script get <host> <port> <username> <password> <item>")
            sys.exit(1)
        print(get_value(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))
