#!/usr/bin/env python3

from datetime import datetime
from sys import argv
import psycopg2
import requests
import config


conn = psycopg2.connect(f"dbname={config.dbname} user={config.user} host={config.host} password={config.password}")
cur = conn.cursor()

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
cur.execute(f'INSERT INTO kociol7_feeder (time, value) VALUES (\'{current_time}\', {argv[1]})')
requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=switchlight&idx={config.domoticz_add_switch_idx}&switchcmd=Set%20Level&level=0')
