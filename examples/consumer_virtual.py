import mb
import time
import random
import logging
import os

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

while True:
    QUEUE_TEST1 = mb.ConnectionPath(mb.MbChannelType.QUEUE, "Consumer.Aaa.VirtualTopic.test1")
    consumer = mb.MbConsumer([QUEUE_TEST1])
    statistics = {"foo": 0}
    while True:
        try:
            msg = consumer.next_message()
            dict = msg.dict()
            logger.info("Received: {}".format(dict))
            statistics['foo'] += 1
            #consumer.ack_message(msg)
            if random.randrange(20) == 1:
                consumer.disconnect()
                pause = random.randrange(60)
                logger.info("Last seen foo value: {}".format(dict['foo']))
                logger.error("There was an artificial error. Reconnect in {} seconds.".format(pause))
                time.sleep(pause)
                break
        except KeyError:
            continue
        except KeyboardInterrupt:
            consumer.disconnect()
            exit(0)
