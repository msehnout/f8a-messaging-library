"""Path generation and utilities."""

from enum import Enum

from mb.error import *


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
        return self.type, self.path


TOPIC_RELEASE_MONITORING_PYPI = ConnectionPath(MbChannelType.TOPIC, "release-monitoring/pypi")
TOPIC_RELEASE_MONITORING_NPM = ConnectionPath(MbChannelType.TOPIC, "release-monitoring/npm")