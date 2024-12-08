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
        
        # Handle different data paths
        if keys[0] == 'STATS':
            stats = data['STATS'][0]  # First element contains all stats
            
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
                # Handle single-level STATS metrics
                metric = keys[1]
                # Convert hyphenated metrics to underscore
                metric_underscore = metric.replace('-', '_')
                
                # First try the original metric name
                if metric in stats:
                    return stats[metric]
                # Then try the underscore version
                elif metric_underscore in stats:
                    return stats[metric_underscore]
        
        logging.error(f"Path not found: {item}")
        return 0
        
    except Exception as e:
        logging.error(f"Error getting value: {str(e)}")
        return 0

def discover_chains(host, port, username, password):
    """
    Returns JSON for Zabbix low-level discovery of chains
    """
    try:
        response = requests.get(
            f'http://{host}:{port}/cgi-bin/stats.cgi',
            auth=HTTPDigestAuth(username, password),
            timeout=5
        )
        data = response.json()
        stats = data['STATS'][0]
        
        discovery = {
            "data": [
                {"{#CHAINID}": str(chain['index'])} 
                for chain in stats['chain']
            ]
        }
        return json.dumps(discovery)
        
    except Exception as e:
        logging.error(f"Error in chain discovery: {str(e)}")
        return json.dumps({"data": []})

def discover_fans(host, port, username, password):
    """
    Returns JSON for Zabbix low-level discovery of fans
    """
    try:
        response = requests.get(
            f'http://{host}:{port}/cgi-bin/stats.cgi',
            auth=HTTPDigestAuth(username, password),
            timeout=5
        )
        data = response.json()
        stats = data['STATS'][0]
        
        discovery = {
            "data": [
                {"{#FANID}": str(i)} 
                for i in range(len(stats['fan']))
            ]
        }
        return json.dumps(discovery)
        
    except Exception as e:
        logging.error(f"Error in fan discovery: {str(e)}")
        return json.dumps({"data": []})

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Discovery: script <discover_chains|discover_fans> <host> <port> <username> <password>")
        print("  Get Value: script get <host> <port> <username> <password> <item>")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action in ["discover_chains", "discover_fans"]:
        if len(sys.argv) != 6:
            print(f"Usage for discovery: script {action} <host> <port> <username> <password>")
            sys.exit(1)
        
        host = sys.argv[2]
        port = sys.argv[3]
        username = sys.argv[4]
        password = sys.argv[5]
        
        if action == "discover_chains":
            print(discover_chains(host, port, username, password))
        else:
            print(discover_fans(host, port, username, password))
            
    elif action == "get":
        if len(sys.argv) != 7:
            print("Usage for getting values: script get <host> <port> <username> <password> <item>")
            sys.exit(1)
        print(get_value(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))
    else:
        print("Unknown action. Use 'discover_chains', 'discover_fans', or 'get'")
        sys.exit(1)
