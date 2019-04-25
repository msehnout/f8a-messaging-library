import os

STOMP_USER: str = os.environ.get('STOMP_USER', 'admin')
STOMP_PASSWORD: str = os.environ.get('STOMP_PASSWORD', 'password')
STOMP_SERVER: str = os.environ.get('STOMP_SERVER', 'localhost')
ENVIRONMENT: str = os.environ.get('ENVIRONMENT', 'staging')