import os

STOMP_USER = os.environ.get('STOMP_USER', 'admin')
STOMP_PASSWORD = os.environ.get('STOMP_PASSWORD', 'password')
STOMP_SERVER = os.environ.get('STOMP_SERVER', 'localhost')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'staging')