import mb
import time
import logging
import os
import random

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)


logging.info("starting")
time.sleep(21)

producer1 = mb.MbProducer(mb.path.TOPIC_RELEASE_MONITORING_NPM)
producer2 = mb.MbProducer(mb.path.TOPIC_RELEASE_MONITORING_PYPI)
while True:
    try:
        producer = random.choice([producer1, producer2])
        msg = '{ "foo": "bar" }'
        producer.publish(msg)
        print("Publishing ...")
        time.sleep(1)
    except KeyboardInterrupt:
        producer.disconnect()
        exit(0)

producer.disconnect()