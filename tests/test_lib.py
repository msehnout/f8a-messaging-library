"""
Test cases for the mq library.

These should approximately cover the intended use cases.
"""
import time
import mb


def test_pub_sub():
    """
    Test publish-subscribe

    Create a blocking consumer and a producer. Produce a message and read it from the topic.
    TODO: ACK the message
    """
    topic_name = "test"
    consumer = mb.MbConsumer(mb.MbChannelType.TOPIC, topic_name)
    producer = mb.MbProducer(mb.MbChannelType.TOPIC, topic_name)
    time.sleep(1.0)
    msg = "hello, world!"
    producer.publish(msg)
    received_msg = consumer.next_message()
    assert received_msg == msg


def test_req_res():
    """
    Test request-response

    Create a callback function for the asynchronous callee and register it. Then create a caller
    and invoke the function over the message bus.
    """
    def cb(user_input):
        if user_input == "1+1":
            return "2"
        else:
            return "error"

    _ = mb.MbRpcCallee('/calc', cb)
    resp = mb.MbRpcCaller.call('/calc', '1+1')
    assert resp == "2"
    resp = mb.MbRpcCaller.call('/calc', '1+2')
    assert resp == "error"


def test_push_pull():
    """
    Test push-pull

    This time create a queue. In a loop push a list of numbers into the queue and on the other side
    just read them all.

    TODO: ACK
    """
    queue_name = "test"
    consumer = mb.MbConsumer(mb.MbChannelType.QUEUE, queue_name)
    producer = mb.MbProducer(mb.MbChannelType.QUEUE, queue_name)
    for i in range(10):
        producer.publish(str(i))

    for i in range(10):
        assert i == int(consumer.next_message())
