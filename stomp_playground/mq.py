"""
Provides unified access to our messaging infrastructure.

Use only this library to interface with our messaging infrastructure, so that we can easily
make changes in the infrastructure and fix code only in one place.
"""
import os
import stomp

from enum import Enum
from random import randrange
from stomp.exception import StompException
from typing import Callable
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
    RPC = 3


def _construct_path(channel_type, path):
    # type: (MqChannelType, str) -> str
    """Create a path string from the input parameters"""
    if path.startswith('/'):
        path = path[1:]
    if channel_type == MqChannelType.TOPIC:
        return "/topic/" + path
    elif channel_type == MqChannelType.QUEUE:
        return "/queue/" + path
    elif channel_type == MqChannelType.RPC:
        return "/temp-queue/" + path
    else:
        raise MqError


class _MqConnector:
    """Base class for all connections."""

    def __init__(self):
        """Construct common connection parameters."""
        try:
            self.connection = stomp.Connection(host_and_ports=[(STOMP_SERVER, 61613)])
            self.connection.connect(STOMP_USER, STOMP_PASSWORD,
                                    wait=True,
                                    headers={
                                        'client-id': 'clientname' # TODO: <- again, put sth better
                                    })
        except StompException:
            raise BrokerConnectionError


class MqProducer(_MqConnector):
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


class MqConsumer(_MqConnector):
    """Use this class to get messages from the broker in a blocking (synchronized) way."""

    def __init__(self, channel_type, path):
        # type: (MqChannelType, str) -> None
        """Create new consumer. By default it is durable and requires ACK on messages."""
        super(MqConsumer, self).__init__()
        self.queue = Queue()
        self.path = _construct_path(channel_type, path)

        headers = dict()
        if channel_type == MqChannelType.TOPIC:
            headers['subscription-type'] = 'MULTICAST'
            headers['durable-subscription-name'] = 'alefjaefli' # TODO: <--

        try:
            self.connection.set_listener('', _StompListener(self.queue))
            self.connection.subscribe(destination=self.path,
                                      id=str(randrange(100000)),
                                      ack='auto',
                                      headers=headers)
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


class MqRpcCaller:
    """Call a remote function and block until its result is available."""

    @staticmethod
    def call(path, request):
        # type: (str, str) -> str
        """
        Call a remote procedure.

        This will enqueue the request and create a temporary queue for the response. Then it
        will wait for the response and return it.
        """
        return_path = "foobarbaz" # TODO: <--
        connector = MqConsumer(MqChannelType.RPC, return_path)
        connector.connection.send(body=request,
                                  destination=_construct_path(MqChannelType.QUEUE, path),
                                  headers={
                                      'reply-to': connector.path
                                  })

        return connector.next_message()


class _StompRpcCallee(stomp.ConnectionListener):
    """Implements listener needed to handle stomp events."""

    def __init__(self, connection, cb):
        self.connection = connection
        self.cb = cb

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        ret = self.cb(message)
        try:
            self.connection.send(body=ret, destination=headers['reply-to'])
        except KeyError:
            pass  # TODO: <--
        except StompException:
            pass  # TODO: <--


class MqRpcCallee(_MqConnector):
    """Define a RPC callee."""

    def __init__(self, path, callback):
        # type: (str, Callable[[str], str]) -> None
        """New callee."""
        super(MqRpcCallee, self).__init__()
        self.path = _construct_path(MqChannelType.QUEUE, path)
        try:
            self.connection.set_listener('', _StompRpcCallee(self.connection, callback))
            self.connection.subscribe(destination=self.path,
                                      id='10'  # TODO: randomize
                                      )
        except StompException:
            raise MqError
