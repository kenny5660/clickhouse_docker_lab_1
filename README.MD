# CLICKHOUSE_DOCKER_LAB_1
* `SEED` - seed for random generator. Default: time.time()
* `VISITORS_PER_HOUR` - visitors per hour. Default: 1000
* `DURATION` - generation duration in hour. Default: 24
* `BUFFER_SIZE` - Buffer size for logger. Default: 10000
```
export SEED=123456
export VISITORS_PER_HOUR=1000
export DURATION=5

docker-compose build
docker-compose up
```

## windows
```
set SEED=123456
set VISITORS_PER_HOUR=1000
set DURATION=5
set BUFFER_SIZE=10000

docker-compose build
docker-compose up
```