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


def test_req_res():
    def cb(user_input):
        if user_input == "1+1":
            return "2"
        else:
            return "error"

    _ = mq.MqRpcCallee('/calc', cb)
    resp = mq.MqRpcCaller.call('/calc', '1+1')
    assert resp == "2"
    resp = mq.MqRpcCaller.call('/calc', '1+2')
    assert resp == "error"
