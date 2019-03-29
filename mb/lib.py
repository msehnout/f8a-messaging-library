"""
Provides unified access to our messaging infrastructure.

Use only this library to interface with our messaging infrastructure, so that we can easily
make changes in the infrastructure and fix code only in one place.
"""

import json
import logging

import stomp


from random import randrange
from stomp.exception import StompException
from typing import Callable, List
from queue import Queue

from mb.error import *
from mb.config import *
from mb.path import *

RAND_RANGE = 1000000

logger = logging.getLogger('mblib')


class MbMessage:
    """Encapsulates a message content and metadata."""

    def __init__(self, msg_id=None, content=None, path=None):
        """Create new message."""
        self.content = content
        self.id = msg_id
        self.path = path

    def dict(self):
        """Try to parse the content as a JSON object."""
        try:
            return json.loads(self.content)
        except json.JSONDecodeError:
            return {}


class _MbConnector:
    """Base class for all connections."""

    def __init__(self, client_id=None):
        """Construct common connection parameters."""
        try:
            self.connection = stomp.Connection(host_and_ports=[(STOMP_SERVER, 61613)])
            if client_id is not None:
                self.client_id = "client_" + client_id
            else:
                self.client_id = "client_" + str(randrange(RAND_RANGE))

            self.connection.connect(STOMP_USER, STOMP_PASSWORD,
                                    wait=True,
                                    headers={
                                        'client-id': self.client_id
                                    })
        except StompException:
            raise BrokerConnectionError

    def disconnect(self):
        self.connection.disconnect()


class MbProducer(_MbConnector):
    """Use this class to publish messages to the broker."""

    def __init__(self, channel_type, path):
        # type: (MbChannelType, str) -> None
        """Create new producer and acquire connection to the broker."""
        super(MbProducer, self).__init__()
        self.path = construct_path(channel_type, path)

    def publish(self, message):
        # type: (str) -> None
        """Publish a message."""
        self.connection.send(body=message, destination=self.path)


class _StompListener(stomp.ConnectionListener):
    """Implements listener needed to handle stomp events."""

    def __init__(self, queue):
        self.queue = queue

    def on_error(self, headers, message):
        logger.error('received an error "%s"' % message)

    def on_message(self, headers, message):
        self.queue.put((headers, message))


class MbConsumer(_MbConnector):
    """Use this class to get messages from the broker in a blocking (synchronized) way."""

    # def __init__(self, channel_type, path, durable_subscription_name=None):
    def __init__(self, listen_on, durable_subscription_name=None):
        # type: (List[(MbChannelType, str)], str) -> None
        """Create new consumer.

        You can choose whether you want to listen on a topic or poll a queue. If you want your
        subscription to be durable, specify the name in arguments.
        """
        super(MbConsumer, self).__init__(client_id=durable_subscription_name)
        self.queue = Queue()

        for channel_type, path in listen_on:
            self.path = construct_path(channel_type, path)

            headers = dict()
            ack_type = 'auto'
            self.subscription_id = "id" + str(randrange(RAND_RANGE))
            if channel_type == MbChannelType.TOPIC:
                headers['subscription-type'] = 'MULTICAST'

                if durable_subscription_name is not None:
                    headers['durable-subscription-name'] = durable_subscription_name
                    ack_type = 'client'
                    self.subscription_id = "subs_id" + durable_subscription_name

            try:
                self.connection.set_listener('', _StompListener(self.queue))
                self.connection.subscribe(destination=self.path,
                                          id=self.subscription_id,
                                          ack=ack_type,
                                          headers=headers)
            except StompException:
                raise MbError

    def next_message(self):
        # type: () -> MbMessage
        """Wait for the next message."""
        headers, content = self.queue.get()
        self.queue.task_done()
        try:
            return MbMessage(msg_id=headers['message-id'], content=content, path=headers['destination'])
        except KeyError:
            MbMessage(content=content)

    def ack_message(self, msg_id):
        # type: (str) -> None
        """Acknowledge a message."""
        self.connection.ack(msg_id, self.subscription_id)


class MbRpcCaller:
    """Call a remote function and block until its result is available."""

    @staticmethod
    def call(path, request):
        # type: (str, str) -> str
        """
        Call a remote procedure.

        This will enqueue the request and create a temporary queue for the response. Then it
        will wait for the response and return it.
        """
        return_path = "return_queue_" + str(randrange(RAND_RANGE))
        connector = MbConsumer([(MbChannelType.RPC, return_path)])
        connector.connection.send(body=request,
                                  destination=construct_path(MbChannelType.QUEUE, path),
                                  headers={
                                      'reply-to': connector.path
                                  })

        return connector.next_message().content


class _StompRpcCallee(stomp.ConnectionListener):
    """Implements listener needed to handle stomp events."""

    def __init__(self, connection, cb):
        self.connection = connection
        self.cb = cb

    def on_error(self, headers, message):
        logger.error('received an error "%s"' % message)

    def on_message(self, headers, message):
        ret = self.cb(message)
        try:
            self.connection.send(body=ret, destination=headers['reply-to'])
        except KeyError:
            logger.error("There is no destination to reply to.")
        except StompException:
            logger.error("stomp.py failed")


class MbRpcCallee(_MbConnector):
    """Define a RPC callee."""

    def __init__(self, path, callback):
        # type: (str, Callable[[str], str]) -> None
        """New callee."""
        super(MbRpcCallee, self).__init__()
        self.path = construct_path(MbChannelType.QUEUE, path)
        try:
            self.connection.set_listener('', _StompRpcCallee(self.connection, callback))
            self.connection.subscribe(destination=self.path,
                                      id="id" + str(randrange(RAND_RANGE))
                                      )
        except StompException:
            raise MbError
