FROM fedora:latest

RUN pip3 install stomp.py
RUN mkdir -p /app
COPY mb /app/mb
COPY collector_example /app/collector_example

WORKDIR /app
CMD ["python3", "-m", "collector_example.rmstub"