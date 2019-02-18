"""
Provides unified access to our messaging infrastructure.

Use only this library to interface with our messaging infrastructure, so that we can easily
make changes in the infrastructure and fix code only in one place.
"""
import os
import stomp

from enum import Enum
from stomp.exception import StompException
from queue import Queue


STOMP_USER = os.environ.get('STOMP_USER', 'admin')
STOMP_PASSWORD = os.environ.get('STOMP_PASSWORD', 'password')
STOMP_SERVER = os.environ.get('STOMP_SERVER', 'localhost')


class MqError(Exception):
    pass


class BrokerConnectionError(MqError):
    pass


class MqChannelType(Enum):
    TOPIC = 1
    QUEUE = 2


def _construct_path(channel_type, path):
    # type: (MqChannelType, str) -> str
    """Create a path string from the input parameters"""
    if path.startswith('/'):
        path = path[1:]
    if channel_type == MqChannelType.TOPIC:
        return "/topic/" + path
    else:
        return "/queue/" + path


class MqConnector:
    """Base class for all connections."""

    def __init__(self):
        try:
            self.connection = stomp.Connection(host_and_ports=[(STOMP_SERVER, 61613)])
            self.connection.connect(STOMP_USER, STOMP_PASSWORD, wait=True)
        except StompException:
            raise BrokerConnectionError


class MqProducer(MqConnector):
    """Use this class to publish messages to the broker."""

    def __init__(self, channel_type, path):
        # type: (MqChannelType, str) -> None
        """Create new producer and acquire connection to the broker."""
        super(MqProducer, self).__init__()
        self.path = _construct_path(channel_type, path)

    def publish(self, message):
        # type: (str) -> None
        """Publish a message."""
        self.connection.send(body=message, destination=self.path)


class _StompListener(stomp.ConnectionListener):
    """Implements listener needed to handle stomp events."""

    def __init__(self, queue):
        self.queue = queue

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        self.queue.put(message)


class MqConsumer(MqConnector):
    """Use this class to get messages from the broker in a blocking way."""

    def __init__(self, channel_type, path):
        # type: (MqChannelType, str) -> None
        """Create new consumer. By default it is durable and requires ACK on messages."""
        super(MqConsumer, self).__init__()
        self.queue = Queue()
        self.path = _construct_path(channel_type, path)
        try:
            self.connection.set_listener('', _StompListener(self.queue))
            self.connection.subscribe(destination=self.path,
                                      id='1',  # TODO: randomize
                                      ack='auto',
                                      headers={
                                          'subscription-type': 'MULTICAST'#,
                                          #'durable-subscription-name': 'alefjaefli'  # TODO: <--
                                      })
        except StompException:
            raise MqError

    def next_message(self):
        # type: () -> str
        """Wait for the next message."""
        ret = self.queue.get()
        self.queue.task_done()
        return ret

    def ack_message(self, msg_id):
        # type: (str) -> None
        """Acknowledge a message."""


class MqRpc:
    """Call a remote function and block until its result is available."""

    def call(self, path, request):
        # type: (str, str) -> str
        """
        Call a remote procedure.

        This will enqueue the request and create a temporary queue for the response. Then it
        will wait for the response and return it.
        """
