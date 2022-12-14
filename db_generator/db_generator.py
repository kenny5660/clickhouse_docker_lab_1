import clickhouse_connect
import time
import traceback
import random
import os


CLICKHOUSE_CONNECT_ATTEMPTS = 10

SEED = os.environ.get('SEED')

if SEED !='':
    print("SEED=",SEED)
    random.seed(int(SEED))

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

#client.command('CREATE TABLE new_table (key UInt32, value String, metric Float64) ENGINE MergeTree ORDER BY key')