import mb
import time
import random
import logging
import os

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
FAILURE_RANGE = int(os.environ.get('FAILURE_RANGE', '50'))
PAUSE_RANGE = int(os.environ.get('PAUSE_RANGE', '20'))
logging.basicConfig(level=LOGLEVEL)

while True:
    QUEUE_TEST1 = mb.path.topic_release_monitoring_pypi_get_listener("Aaa")
    consumer = mb.MbConsumer([QUEUE_TEST1])
    statistics = {"foo": 0}
    while True:
        try:
            msg = consumer.next_message()
            dict = msg.dict()
            logger.info("Received: {}".format(dict))
            statistics['foo'] += 1
            #consumer.ack_message(msg)
            if random.randrange(FAILURE_RANGE) == 1:
                consumer.disconnect()
                pause = random.randrange(PAUSE_RANGE)
                logger.info("Last seen foo value: {}".format(dict['foo']))
                logger.error("There was an artificial error. Reconnect in {} seconds.".format(pause))
                time.sleep(pause)
                break
        except KeyError:
            continue
        except KeyboardInterrupt:
            consumer.disconnect()
            exit(0)
