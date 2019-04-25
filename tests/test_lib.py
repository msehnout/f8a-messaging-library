"""
Test cases for the mq library.

These should approximately cover the intended use cases.
"""
import f8a_mb
import multiprocessing
import time


def test_pub_sub():
    """
    Test publish-subscribe

    Create a blocking consumer and a producer. Produce a message and read it from the topic.
    """
    topic_name = "test"
    consumer = f8a_mb.MbConsumer([f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, topic_name)])
    producer = f8a_mb.MbProducer(f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, topic_name))
    time.sleep(1.0)
    msg = "hello, world!"
    producer.publish(msg)
    received_msg = consumer.next_message().content
    assert received_msg == msg


def test_multiple_pub_single_sub():
    """Test publish-subscribe for multiple publishers and a single consumer."""
    producers = [f8a_mb.MbProducer(f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, "mpss1")),
                 f8a_mb.MbProducer(f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, "mpss2")),
                 f8a_mb.MbProducer(f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, "mpss3")),
                 f8a_mb.MbProducer(f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, "mpss4"))]
    time.sleep(1.0)
    consumer = f8a_mb.MbConsumer([f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, "mpss1"),
                                  f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, "mpss2"),
                                  f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, "mpss3"),
                                  f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, "mpss4")])
    time.sleep(1.0)

    for i, p in enumerate(producers):
        p.publish(str(i+1))

    for i in range(4):
        msg = consumer.next_message()
        path = msg.path
        content = msg.content
        # what is that? the path ends with a number and the message is that number -1
        assert int(path[-1]) == int(content)


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

    _ = f8a_mb.MbRpcCallee('/calc', cb)
    resp = f8a_mb.MbRpcCaller.call('/calc', '1+1')
    assert resp == "2"
    resp = f8a_mb.MbRpcCaller.call('/calc', '1+2')
    assert resp == "error"


def test_push_pull():
    """
    Test push-pull

    This time create a queue. In a loop push a list of numbers into the queue and on the other side
    just read them all.
    """
    queue_name = "test"
    consumer = f8a_mb.MbConsumer([f8a_mb.ConnectionPath(f8a_mb.MbChannelType.QUEUE, queue_name)])
    time.sleep(1)
    producer = f8a_mb.MbProducer(f8a_mb.ConnectionPath(f8a_mb.MbChannelType.QUEUE, queue_name))
    for i in range(10):
        producer.publish(str(i))

    for i in range(10):
        assert i == int(consumer.next_message().content)


def test_durability():
    """Test durable subscription."""
    topic_name = "durability_test"
    testing_msg = "ahoj123"

    def create_consumer():
        nonlocal topic_name
        consumer = f8a_mb.MbConsumer([f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC,
                                                            topic_name)],
                                     durable_subscription_names="durability_test_123456")
        return consumer

    def just_create_it_and_do_nothing():
        consumer = create_consumer()
        while True:
            time.sleep(10)

    def read_msg_and_check_it():
        nonlocal testing_msg
        consumer = create_consumer()
        assert consumer.next_message().content == testing_msg

    p = multiprocessing.Process(target=just_create_it_and_do_nothing)
    p.start()
    time.sleep(5)
    p.terminate()
    p.join()
    time.sleep(10)

    producer = f8a_mb.MbProducer(f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, topic_name))
    producer.publish(testing_msg)
    time.sleep(1)

    p = multiprocessing.Process(target=read_msg_and_check_it)
    p.start()
    p.join(5)

    if p.is_alive():
        p.terminate()
        p.join()
        assert False


def test_topic_redelivery():
    """Test durable subscription with redelivery."""
    topic_name = "redelivery_test"
    durable_subscription_name = "redelivery_test_123456"

    def create_consumer():
        consumer = f8a_mb.MbConsumer([f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC,
                                                            topic_name)],
                                     durable_subscription_names=durable_subscription_name)
        return consumer

    def cleanup_subscription():
        consumer = create_consumer()
        while True:
            msg = consumer.next_message()
            consumer.ack_message(msg)

    def consume_half_of_the_messages():
        consumer = create_consumer()

        for i in range(0, 5):
            msg = consumer.next_message()
            assert str(i) == msg.content
            consumer.ack_message(msg)

        for i in range(5, 10):
            msg = consumer.next_message()
            assert str(i) == msg.content

        while True:
            time.sleep(10)

    def consume_rest():
        consumer = create_consumer()

        for i in range(5, 10):
            msg = consumer.next_message()
            assert str(i) == msg.content
            consumer.ack_message(msg)

    p = multiprocessing.Process(target=cleanup_subscription)
    p.start()
    time.sleep(5)
    p.terminate()
    p.join()

    p = multiprocessing.Process(target=consume_half_of_the_messages)
    p.start()

    producer = f8a_mb.MbProducer(f8a_mb.ConnectionPath(f8a_mb.MbChannelType.TOPIC, topic_name))
    for i in range(0, 10):
        producer.publish(str(i))

    time.sleep(5)
    if not p.is_alive():
        assert False

    p.terminate()
    p.join()
    time.sleep(10)

    p = multiprocessing.Process(target=consume_rest)
    p.start()
    p.join(5)

    if p.is_alive():
        p.terminate()
        p.join()
        assert False
