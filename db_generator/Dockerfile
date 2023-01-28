FROM python:3.10-bullseye
RUN pip install clickhouse-connect==0.5.2 simpy==4.0.1 numpy==1.21.5
COPY db_generator.py ./
COPY logger.py ./
COPY web_site_sim.py ./
COPY user_agent_top_50.txt ./
