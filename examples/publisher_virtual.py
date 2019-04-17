import mb
import time
import logging
import os
import random

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)


logging.info("starting")

TOPIC_TEST1 = mb.ConnectionPath(mb.MbChannelType.TOPIC, "VirtualTopic.test1")
#TOPIC_TEST1 = mb.ConnectionPath(mb.MbChannelType.QUEUE, "Consumer.aaa.VirtualTopic.test1")
producer = mb.MbProducer(TOPIC_TEST1)
counter = 0
while True:
    try:
        msg = '{ "foo": "' + str(counter) + '" }'
        producer.publish(msg)
        print("Publishing ..." + str(counter))
        time.sleep(2)
        counter += 1
    except KeyboardInterrupt:
        producer.disconnect()
        exit(0)
