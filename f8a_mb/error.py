"""Predefined errors used in this library."""


class MbError(Exception):
    """Base error."""
    pass


class BrokerConnectionError(MbError):
    """Failed connection to the broker."""
    # NOTE: in theory you don't need to handle this one, because OpenShift will restart your service
    # as soon as it fails with this error
    pass
