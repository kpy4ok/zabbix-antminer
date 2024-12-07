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
        if keys[0] == 'STATUS':
            return data['STATUS']['STATUS']
        elif keys[0] == 'INFO':
            return data['INFO'][keys[1]]
        elif keys[0] == 'STATS':
            stats = data['STATS'][0]  # First element contains all stats
            
            # Handle chain-specific data
            if 'chain' in keys:
                chain_index = int(keys[2])
                chain = stats['chain'][chain_index]
                
                if keys[1] == 'temp_chip':
                    return chain['temp_chip'][int(keys[3])]
                elif keys[1] == 'temp_pcb':
                    return chain['temp_pcb'][int(keys[3])]
                elif keys[1] == 'temp_pic':
                    return chain['temp_pic'][int(keys[3])]
                elif keys[1] == 'rate':
                    return chain['rate_real']
                elif keys[1] == 'freq':
                    return chain['freq_avg']
                elif keys[1] == 'hw_errors':
                    return chain['hw']
                elif keys[1] == 'asic_num':
                    return chain['asic_num']
                
            # Handle fan data
            elif 'fan' in keys:
                fan_index = int(keys[2])
                return stats['fan'][fan_index]
                
            # Handle general stats
            else:
                if keys[1] == 'rate_5s':
                    return stats['rate_5s']
                elif keys[1] == 'rate_30m':
                    return stats['rate_30m']
                elif keys[1] == 'rate_avg':
                    return stats['rate_avg']
                elif keys[1] == 'rate_ideal':
                    return stats['rate_ideal']
                elif keys[1] == 'elapsed':
                    return stats['elapsed']
                elif keys[1] == 'fan_num':
                    return stats['fan_num']
                elif keys[1] == 'chain_num':
                    return stats['chain_num']
                elif keys[1] == 'hwp_total':
                    return stats['hwp_total']
                elif keys[1] == 'miner_mode':
                    return stats['miner-mode']
                elif keys[1] == 'freq_level':
                    return stats['freq-level']
                
        return 0
        
    except Exception as e:
        logging.error(f"Error getting value: {str(e)}")
        return 0

def discovery_chains():
    """
    Returns JSON for Zabbix low-level discovery of chains
    """
    try:
        response = requests.get(
            f'http://{sys.argv[2]}:{sys.argv[3]}/cgi-bin/stats.cgi',
            auth=HTTPDigestAuth(sys.argv[4], sys.argv[5]),
            timeout=5
        )
        data = response.json()
        chains = data['STATS'][0]['chain_num']
        
        discovery = {
            "data": [
                {"{#CHAINID}": chain_id} for chain_id in range(chains)
            ]
        }
        return json.dumps(discovery)
        
    except Exception as e:
        logging.error(f"Error in chain discovery: {str(e)}")
        return json.dumps({"data": []})

def discover_fans():
    """
    Returns JSON for Zabbix low-level discovery of fans
    """
    try:
        response = requests.get(
            f'http://{sys.argv[2]}:{sys.argv[3]}/cgi-bin/stats.cgi',
            auth=HTTPDigestAuth(sys.argv[4], sys.argv[5]),
            timeout=5
        )
        data = response.json()
        fans = data['STATS'][0]['fan_num']
        
        discovery = {
            "data": [
                {"{#FANID}": fan_id} for fan_id in range(fans)
            ]
        }
        return json.dumps(discovery)
        
    except Exception as e:
        logging.error(f"Error in fan discovery: {str(e)}")
        return json.dumps({"data": []})

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    
    if len(sys.argv) < 6:
        print("Usage: script <action> <host> <port> <username> <password> [item]")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "discovery_chains":
        print(discovery_chains())
    elif action == "discover_fans":
        print(discover_fans())
    else:
        if len(sys.argv) != 7:
            print("Usage for getting values: script get <host> <port> <username> <password> <item>")
            sys.exit(1)
        print(get_value(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))
