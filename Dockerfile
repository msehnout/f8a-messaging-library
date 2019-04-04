FROM fedora:latest

RUN pip3 install stomp.py
RUN mkdir -p /app
WORKDIR /app
COPY . .

CMD ["python3", "-m", "examples.rmstub"]
