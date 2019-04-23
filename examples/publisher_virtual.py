import mb
import time
import logging
import os

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
PAUSE = int(os.environ.get('PAUSE', '15'))

logging.basicConfig(level=LOGLEVEL)


logging.info("starting")

TOPIC_TEST1 = mb.ConnectionPath(mb.MbChannelType.TOPIC, "VirtualTopic.test1")
producer = mb.MbProducer(TOPIC_TEST1)
counter = 0
while True:
    try:
        msg = '{ "foo": "' + str(counter) + '" }'
        producer.publish(msg)
        logger.info("Publishing ..." + str(counter))
        time.sleep(PAUSE)
        counter += 1
    except KeyboardInterrupt:
        producer.disconnect()
        exit(0)
