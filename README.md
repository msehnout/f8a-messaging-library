# Message Bus (MB) library

A Python library for interfacing with a message broker. It should be 
compatible with anything based on ActiveMQ like AmazonMQ or Red Hat
AMQ, but I test it only with Red Hat AMQ.

### Architecture

The `mb` library is a thin wrapper around [stomp.py](https://pypi.org/project/stomp.py/).
It covers the underlying protocol and exposes only classes for common
use cases like:
 * publish/subscribe
 * push/pull
 * RPC

They can be either synchronous or asynchronous (callback based).

### Configuration

The configuration is based on environment variable because I want to deploy
the library into OpenShift (Kubernetes) and I don't want to deal with
configuration in the code. It also hides a lot of configuration options
and exposes only one way to interface with the messaging infrastructure.

### Example

Find examples [here](examples/).

### Complex example

Run:
```text
$ docker-compose build && docker-compose up
```

This will spin up example collector and message producer together with a broker.
From this simulation you can get a gist of how to deploy clients using the library.
See the `docker-compose.yml` file for configuration. This would be configured in
an OpenShift template.

### Testing

To try it locally, run the broker first:
```
$ docker run -p 61613:61613 -e AMQ_USER=user -e AMQ_PASSWORD=redhat -e AMQ_PROTOCOL=stomp -e ADMIN_PASSWORD=redhat registry.access.redhat.com/amq-broker-7/amq-broker-72-openshift
```
Then run the tests themselves:
```
$ pytest tests
```