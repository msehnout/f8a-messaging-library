"""
Provides unified access to our messaging infrastructure.

Use only this library to interface with our messaging infrastructure, so that we can easily
make changes in the infrastructure and fix code only in one place.
"""
from enum import Enum


class BrokerConnectionError(Exception):
    pass


class MqChannelType(Enum):
    TOPIC = 1
    QUEUE = 2


class MqProducer:
    """Use this class to publish messages to the broker."""

    def __init__(self, channel_type, path):
        # type: (MqChannelType, str) -> None
        """Create new producer and acquire connection to the broker."""
        raise BrokerConnectionError

    def publish(self, message):
        # type: (str) -> None
        """
        Publish a message.
        """
        pass


class MqConsumer:
    """Use this class to get messages from the broker in a blocking way."""

    def __init__(self, channel_type, path):
        # type: (MqChannelType, str) -> None
        """Create new consumer. By default it is durable and requires ACK on messages."""

    def next_message(self):
        # type: () -> str
        """Wait for the next message."""

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
