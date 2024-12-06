#!/usr/bin/env python
import logging
import requests
from requests.auth import HTTPDigestAuth
import json
from datetime import timedelta
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init()

# Hardcoded credentials and connection details
HOST = "192.168.1.110"
PORT = "80"
USERNAME = "root"
PASSWORD = "root"

# Temperature thresholds
TEMP_WARN = 75
TEMP_CRIT = 85

def format_temp(temp):
    """Format temperature with color coding"""
    if temp >= TEMP_CRIT:
        return f"{Fore.RED}{temp:3d}°C{Style.RESET_ALL}"
    elif temp >= TEMP_WARN:
        return f"{Fore.YELLOW}{temp:3d}°C{Style.RESET_ALL}"
    return f"{Fore.GREEN}{temp:3d}°C{Style.RESET_ALL}"

def format_uptime(seconds):
    """Convert seconds to human readable uptime"""
    return str(timedelta(seconds=seconds))

def format_hashrate(hashrate, unit="GH/s"):
    """Format hashrate with color based on ideal vs real"""
    return f"{hashrate:,.2f} {unit}"

def get_miner_status():
    """
    Retrieves and displays status information from Antminer S19k Pro
    """
    try:
        url = f'http://{HOST}:{PORT}/cgi-bin/stats.cgi'
        print(f"Connecting to miner at: {url}")
        
        response = requests.get(
            url,
            auth=HTTPDigestAuth(USERNAME, PASSWORD),
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data['STATS'][0]
            
            print(f"\n{Fore.CYAN}Miner Information:{Style.RESET_ALL}")
            print("-" * 50)
            print(f"Model: {data['INFO']['type']}")
            print(f"Firmware Version: {data['INFO']['miner_version']}")
            print(f"Compile Time: {data['INFO']['CompileTime']}")
            print(f"Uptime: {format_uptime(stats['elapsed'])}")
            print(f"Operating Mode: {'Normal' if stats['miner-mode'] == 0 else 'Other'}")
            print(f"Frequency Level: {stats['freq-level']}%")
            
            print(f"\n{Fore.CYAN}Hashrate Information:{Style.RESET_ALL}")
            print("-" * 50)
            print(f"5s Hashrate:    {format_hashrate(stats['rate_5s'])}")
            print(f"30m Hashrate:   {format_hashrate(stats['rate_30m'])}")
            print(f"Average Rate:   {format_hashrate(stats['rate_avg'])}")
            print(f"Ideal Rate:     {format_hashrate(stats['rate_ideal'])}")
            print(f"Hardware Error Rate: {Fore.GREEN}{stats['hwp_total']}%{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}Fan Status:{Style.RESET_ALL}")
            print("-" * 50)
            print(f"Number of Fans: {stats['fan_num']}")
            for i, speed in enumerate(stats['fan'], 1):
                color = Fore.GREEN if speed > 4000 else Fore.YELLOW if speed > 3000 else Fore.RED
                print(f"Fan {i} Speed: {color}{speed:4d} RPM{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}Chain Information:{Style.RESET_ALL}")
            print("-" * 50)
            
            for chain in stats['chain']:
                print(f"\n{Fore.YELLOW}Chain {chain['index']}:{Style.RESET_ALL}")
                print(f"Serial Number: {chain['sn']}")
                print(f"Frequency: {chain['freq_avg']} MHz")
                
                # Calculate efficiency percentage
                efficiency = (chain['rate_real'] / chain['rate_ideal']) * 100
                efficiency_color = Fore.GREEN if efficiency >= 98 else Fore.YELLOW if efficiency >= 95 else Fore.RED
                
                print(f"Real Hashrate:  {format_hashrate(chain['rate_real'])}")
                print(f"Ideal Hashrate: {format_hashrate(chain['rate_ideal'])}")
                print(f"Efficiency: {efficiency_color}{efficiency:.1f}%{Style.RESET_ALL}")
                print(f"Number of ASICs: {chain['asic_num']}")
                print(f"Hardware Errors: {Fore.GREEN if chain['hw'] == 0 else Fore.RED}{chain['hw']}{Style.RESET_ALL}")
                
                print("\nTemperatures:")
                print("Chip:  " + " ".join(format_temp(temp) for temp in chain['temp_chip']))
                print("PCB:   " + " ".join(format_temp(temp) for temp in chain['temp_pcb']))
                print("PIC:   " + " ".join(format_temp(temp) for temp in chain['temp_pic']))
            
            return data
            
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Connection error: {str(e)}{Style.RESET_ALL}")
        return None
    except ValueError as e:
        print(f"{Fore.RED}JSON parsing error: {str(e)}{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        return None

def main():
    logging.basicConfig(level=logging.INFO)
    print(f"{Fore.CYAN}Checking Antminer S19k Pro status...{Style.RESET_ALL}")
    get_miner_status()

if __name__ == '__main__':
    main()
