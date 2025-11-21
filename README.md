# zabbix-antminer
Status script for Antminer to monitor with Zabbix 5

# Tested with: 

* Anminer S19K Pro

# How it works

* Get AntMiner metrics from `/cgi-bin/get_miner_status.cgi` output by HTTP
* Parse data from JSON output
* Store data into Zabbix

# You can start with:

* You can test your connecton buy typing: python3 console.py
* Be sure to edit host user and password section in console.py before running

# Install
* Download antminer.py and zbx_antminer_template.xml
* Put antminer.py into ExternalScript location (usual /usr/lib/zabbix/externalscripts)
* Make antminer.py executable (`chmod 755 antminer.py`)
* Import zabbix_template (zbx_antminer_template.xml) into zabbix
* Add AntMiner as Zabbix Host. Use Zabbix Agent type.
* Add Zabbix Macros `{$MINER.PORT}` with AntMiner HTTP port value if your port differ from 80.
* Add Zabbix Macros `{$MINER.USERNAME}` with AntMiner HTTP Username if your user differ from root.
* Add Zabbix Macros `{$MINER.PASS}` with AntMiner HTTP Password if your pass differ from root.
* Link template to You machine.

# Inspired by
* https://github.com/dysnix/zabbix-antminer/
