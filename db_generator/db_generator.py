import clickhouse_connect
import time
import traceback
import random
import os
import web_site_sim


CLICKHOUSE_CONNECT_ATTEMPTS = 10

SEED = os.environ.get('SEED')
VISITORS_PER_HOUR = os.environ.get('VISITORS_PER_HOUR')
DURATION = os.environ.get('DURATION')

if SEED !=''and not SEED is None:
    print("SEED=",SEED)
    SEED = int(SEED)

if VISITORS_PER_HOUR !='' and not VISITORS_PER_HOUR is None:
    print("VISITORS_PER_HOUR=",VISITORS_PER_HOUR)
    VISITORS_PER_HOUR = int(VISITORS_PER_HOUR)
else:
    VISITORS_PER_HOUR = 1000

if DURATION !='' and not DURATION is None:
    print("DURATION=",DURATION)
    DURATION = float(DURATION)*3600
else:
    DURATION = 24*3600

print("run db_generator")
for i in range(0,CLICKHOUSE_CONNECT_ATTEMPTS+1):
    time.sleep(0.5)
    try:
        client = clickhouse_connect.get_client()
        break
    except Exception:
        if i >= CLICKHOUSE_CONNECT_ATTEMPTS:
            #traceback.print_exc()
            print("connection error")
            exit(-1)
            
print("connected to clickhouse-server version:",client.server_version) 

client.command('''CREATE DATABASE IF NOT EXISTS log_storage''')
client.command('''DROP TABLE IF EXISTS log_storage.logs_app''')
client.command('''CREATE TABLE log_storage.logs_app(
`timestamp` DateTime,
`request` String,
`request_method` String,
`http_status` Int,
`user_agent` String,
`user_ip` String,
`request_time` Float32)
       ENGINE = MergeTree()
       PARTITION BY toYYYYMM(timestamp)
       ORDER BY (timestamp, request, request_method,user_ip);''')
start_time = time.time()
logger = web_site_sim.ClickhouseLogger(client,'log_storage.logs_app')
web_site_sim.generate_logs(logger,SEED,VISITORS_PER_HOUR,DURATION)
logger._send_buffer()
exec_time = time.time() - start_time
print("Generation compleate!!! time: %f sec"%(exec_time))