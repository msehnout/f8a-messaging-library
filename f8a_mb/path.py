"""
Path generation and utilities.

This module exists so that you don't have to write paths such as /topic/release-monitoring/pypi by
hand. This comes with several benefits:
 * it prevents human errors such as typos
 * it provides forward compatibility as you are abstracted away from the broker usage details
 * we have a single place to enforce consistent naming across the whole platform
"""

from enum import Enum

from f8a_mb.error import *
from f8a_mb.config import ENVIRONMENT


class MbChannelType(Enum):
    """Define possible types of communication.

    pub-sub => topic
    push-pull => queue
    req-res => rpc
    """
    TOPIC = 1
    QUEUE = 2
    RPC = 3


def construct_path(channel_type, path):
    # type: (MbChannelType, str) -> str
    """Create a path string from the input parameters"""
    if path.startswith('/'):
        path = path[1:]

    mapping = {
        MbChannelType.TOPIC: "/topic/" + path,
        MbChannelType.QUEUE: "/queue/" + path,
        MbChannelType.RPC: "/temp-queue/" + path
    }

    try:
        return mapping[channel_type]
    except KeyError:
        raise MbError


class ConnectionPath:
    """Encapsulates connection path into typed object as opposed to plain string."""

    def __init__(self, type, path):
        """Create a connection path."""
        self.path = construct_path(type, path)
        self.type = type

    def as_tuple(self):
        """Return path as a tuple."""
        return self.type, self.path


TOPIC_RELEASE_MONITORING_PYPI: ConnectionPath = \
    ConnectionPath(MbChannelType.TOPIC,
                   "VirtualTopic.{}.release-monitoring.PyPI".format(ENVIRONMENT))
TOPIC_RELEASE_MONITORING_NPM: ConnectionPath = \
    ConnectionPath(MbChannelType.TOPIC,
                   "VirtualTopic.{}.release-monitoring.NPM".format(ENVIRONMENT))


def topic_release_monitoring_pypi_get_listener(name: str):
    """Get a consumer path for PyPI release monitoring containing the given name."""
    return ConnectionPath(MbChannelType.QUEUE,
                          "Consumer.{}.VirtualTopic.{}.release-monitoring.PyPI"
                          .format(name, ENVIRONMENT))


def topic_release_monitoring_npm_get_listener(name: str):
    """Get a consumer path for NPM release monitoring  containing the given name."""
    return ConnectionPath(MbChannelType.QUEUE,
                          "Consumer.{}.VirtualTopic.{}.release-monitoring.NPM"
                          .format(name, ENVIRONMENT))