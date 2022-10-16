#!/usr/bin/env python3

from datetime import datetime
import paho.mqtt.client as mqtt
import psycopg2
import config


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("esp8266/kociol")


def on_message(client, userdata, message):
    payload = int(message.payload.decode())
    if payload > 1000:  # LEDs blink for a short time on power-on, we don't want to count that
        conn = psycopg2.connect(f"dbname={config.dbname} user={config.user} host={config.host} password={config.password}")
        cur = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(timestamp, payload)
        cur.execute("INSERT INTO kociol7 (measurement_time, measurement_value) VALUES (%s, %s)", (timestamp, payload))
        conn.commit()
        conn.close()


conn = psycopg2.connect(f"dbname={config.dbname} user={config.user} host={config.host} password={config.password}")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS kociol7 (id serial PRIMARY KEY, measurement_time timestamp, measurement_value integer);")
conn.commit()
conn.close()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config.mqtt_host, config.mqtt_port, 60)
client.loop_forever()
