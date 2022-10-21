#!/usr/bin/env python3

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import psycopg2
import requests
import config

conn = psycopg2.connect(f"dbname={config.dbname} user={config.user} host={config.host} password={config.password}")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS kociol7_feeder (id SERIAL PRIMARY KEY, time timestamp, value integer);")
conn.commit()

time_now = datetime.now()

start_time = (time_now - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S.%f')
end_time = time_now.strftime('%Y-%m-%d %H:%M:%S.%f')
cur.execute(f'SELECT SUM(measurement_value) FROM kociol7 WHERE measurement_time > \'{start_time}\' AND measurement_time < \'{end_time}\';')
last24h_avg_query = cur.fetchone()[0]
last24h_avg = 0
if last24h_avg_query is not None:
    last24h_avg = last24h_avg_query / config.milliseconds_per_1g / 1000 / 3
    last24h_avg = round(last24h_avg, 2)

start_time = (time_now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S.%f')
cur.execute(f'SELECT SUM(measurement_value) FROM kociol7 WHERE measurement_time > \'{start_time}\' AND measurement_time < \'{end_time}\';')
last24h_query = cur.fetchone()[0]
last24h = 0
if last24h_query is not None:
    last24h = last24h_query / config.milliseconds_per_1g / 1000
    last24h = round(last24h, 2)

if time_now.month < 9:
    start_time = (time_now.replace(month=9, day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(years=1)).strftime('%Y-%m-%d %H:%M:%S.%f')
else:
    start_time = (time_now.replace(month=9, day=1, hour=0, minute=0, second=0, microsecond=0)).strftime('%Y-%m-%d %H:%M:%S.%f')
cur.execute(f'SELECT SUM(measurement_value) FROM kociol7 WHERE measurement_time > \'{start_time}\' AND measurement_time < \'{end_time}\';')
from_september_query = cur.fetchone()[0]
from_september = 0
if from_september_query is not None:
    from_september = from_september_query / config.milliseconds_per_1g / 1000
    from_september = round(from_september, 2)

cur.execute(f'SELECT SUM(value) FROM kociol7_feeder WHERE time > \'{start_time}\' AND time < \'{end_time}\';')
from_september_feeder_query = cur.fetchone()[0]
from_september_feeder = 0
if from_september_feeder_query is not None:
    from_september_feeder = from_september_feeder_query
feeder_left = from_september_feeder - from_september

if config.domoticz_enabled:
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_last24h_avg_idx}&nvalue=0&svalue={last24h_avg}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_from_septeber_idx}&nvalue=0&svalue={from_september}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_feeder_left_idx}&nvalue=0&svalue={feeder_left}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_last24h_idx}&nvalue=0&svalue={last24h}')
