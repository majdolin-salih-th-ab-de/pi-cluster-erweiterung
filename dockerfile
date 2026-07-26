FROM python:3.13.1-slim

WORKDIR /src

COPY requirements.txt /src
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /src/

CMD ["sh", "-c", "while true; do sleep 1; done"]

# docker build -t pi_cluster:latest . 