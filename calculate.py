from datetime import datetime, timedelta
import psycopg2
import config

conn = psycopg2.connect(f"dbname={config.dbname} user={config.user} host={config.host} password={config.password}")
cur = conn.cursor()

start_time = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S.%f')
end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
cur.execute(f'SELECT SUM(measurement_value) FROM kociol7 WHERE measurement_time > \'{start_time}\' AND measurement_time < \'{end_time}\';')
last72h_rolling_avg = cur.fetchone()[0] / config.miliseconds_per_1g / 1000 / 3
print(last72h_rolling_avg)
