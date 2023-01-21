# CLICKHOUSE_DOCKER_LAB_1
* `SEED` - seed for random generator
* `VISITORS_PER_HOUR` - visitors per hour
* `DURATION` - generation duration in hour
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

docker-compose build
docker-compose up
```