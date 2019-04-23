import mb
import time
import logging
import os

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

QUEUE_TEST1 = mb.ConnectionPath(mb.MbChannelType.QUEUE, "Consumer.Aaa.VirtualTopic.test1")
consumer = mb.MbConsumer([QUEUE_TEST1])
statistics = {"foo": 0}
counter = 0
while True:
    try:
        msg = consumer.next_message()
        dict = msg.dict()
        print("Received: {}".format(dict))
        statistics['foo'] += 1
        #consumer.ack_message(msg)
        counter += 1
        if counter % 2 == 0:
            pass # time.sleep(3)
    except KeyError:
        continue
    except KeyboardInterrupt:
        consumer.disconnect()
        exit(0)
