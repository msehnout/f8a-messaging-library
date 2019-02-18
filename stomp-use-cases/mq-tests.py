"""
Test cases for the mq library.

These should approximately cover the intended use cases.
"""
from . import mq


def test_pub_sub():
    consumer = mq.MqConsumer(mq.MqChannelType.TOPIC, "/foo")
    producer = mq.MqProducer(mq.MqChannelType.TOPIC, "/foo")
    msg = "hello, world!"
    producer.publish(msg)
    received_msg = consumer.next_message()
    assert received_msg == msg
