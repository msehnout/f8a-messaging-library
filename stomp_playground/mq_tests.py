"""
Test cases for the mq library.

These should approximately cover the intended use cases.
"""
import time

from . import mq


def test_pub_sub():
    topic_name = "test"
    consumer = mq.MqConsumer(mq.MqChannelType.TOPIC, topic_name)
    producer = mq.MqProducer(mq.MqChannelType.TOPIC, topic_name)
    time.sleep(1.0)
    msg = "hello, world!"
    producer.publish(msg)
    received_msg = consumer.next_message()
    assert received_msg == msg
