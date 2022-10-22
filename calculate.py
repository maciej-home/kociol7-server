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

start_time = (time_now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S.%f')
cur.execute(f'SELECT SUM(measurement_value) FROM kociol7 WHERE measurement_time > \'{start_time}\' AND measurement_time < \'{end_time}\';')
last6h_query = cur.fetchone()[0]
last6h = 0
if last6h_query is not None:
    last6h = last6h_query / config.milliseconds_per_1g / 1000
boiler_power = last6h * config.coal_megajoules * 1000000 / (6 * 3600)
boiler_power_kw = round(boiler_power / 1000, 1)

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

start_time = (time_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)).strftime('%Y-%m-%d %H:%M:%S.%f')
cur.execute(f'SELECT SUM(measurement_value) FROM kociol7 WHERE measurement_time > \'{start_time}\' AND measurement_time < \'{end_time}\';')
current_month_query = cur.fetchone()[0]
current_month = 0
if current_month_query is not None:
    current_month = current_month_query / config.milliseconds_per_1g / 1000
    current_month = round(current_month, 0)

start_time = (time_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S.%f')
end_time = (time_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)).strftime('%Y-%m-%d %H:%M:%S.%f')
cur.execute(f'SELECT SUM(measurement_value) FROM kociol7 WHERE measurement_time > \'{start_time}\' AND measurement_time < \'{end_time}\';')
last_month_query = cur.fetchone()[0]
last_month = 0
if last_month_query is not None:
    last_month = last_month_query / config.milliseconds_per_1g / 1000
    last_month = round(last_month, 0)

days_left = feeder_left / last24h_avg
hours_left = days_left * 24
if hours_left < 10:
    hours_left = round(hours_left, 1)
else:
    hours_left = round(hours_left, 0)
days_left = round(days_left, 0)

if config.domoticz_enabled:
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_last24h_avg_idx}&nvalue=0&svalue={last24h_avg}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_from_septeber_idx}&nvalue=0&svalue={from_september}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_feeder_left_idx}&nvalue=0&svalue={feeder_left}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_last24h_idx}&nvalue=0&svalue={last24h}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_days_left_idx}&nvalue=0&svalue={days_left}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_hours_left_idx}&nvalue=0&svalue={hours_left}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_boiler_power_idx}&nvalue=0&svalue={boiler_power_kw}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_last_month_idx}&nvalue=0&svalue={last_month}')
    requests.get(f'http://{config.domoticz_host}:{config.domoticz_port}/json.htm?type=command&param=udevice&idx={config.domoticz_current_month_idx}&nvalue=0&svalue={current_month}')
