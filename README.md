# AMQ Deployment and use cases

## Part I: Message bus library

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
configuration in the code.

### Example

Simple pub/sub use case:
```python
import time
import mb

topic_name = "test"
# Note that no configuration is required because it is done in the
# OpenShift template therefore it would be redundant to do it here
consumer = mb.MbConsumer(mb.MbChannelType.TOPIC, topic_name)
producer = mb.MbProducer(mb.MbChannelType.TOPIC, topic_name)
time.sleep(1.0)
msg = "hello, world!"
producer.publish(msg)
# This is a blocking consumer, you can consume messages in a loop
received_msg = consumer.next_message()
assert received_msg == msg
```

### Testing

To try it locally, run the broker first:
```
$ docker run -p 61613:61613 -e AMQ_USER=user -e AMQ_PASSWORD=redhat -e AMQ_PROTOCOL=stomp -e ADMIN_PASSWORD=redhat registry.access.redhat.com/amq-broker-7/amq-broker-72-openshift
```
Then run the tests themselves:
```
$ pytest tests
```

## Part II: AMQP

```
docker run -p 8161:8161 -p 5671:5671 -p 5672:5672 -p 61613:61613 -e AMQ_USER=user -e AMQ_PASSWORD=redhat -e AMQ_PROTOCOL=amqp,stomp -e AMQ_QUEUES=foo -e AMQ_ADDRESSES=bar -e ADMIN_PASSWORD=redhat registry.access.redhat.com/amq-broker-7/amq-broker-72-openshift
qb message receive  -b 127.0.0.1:5672 -c 10 topic://amq.topic/example
qb message send -b 127.0.0.1:5672 topic://amq.topic/example ahoj
```
