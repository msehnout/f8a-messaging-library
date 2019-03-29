import mb
import time
import logging
import os

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)


logging.info("starting")
time.sleep(21)

for topic in [mb.path.TOPIC_RELEASE_MONITORING_NPM, mb.path.TOPIC_RELEASE_MONITORING_PYPI]:
    producer = mb.MbProducer(mb.MbChannelType.TOPIC, topic)
    for _ in range(10):
        try:
            msg = '{ "foo": "bar" }'
            producer.publish(msg)
            print("Publishing ...")
            time.sleep(5)
        except KeyboardInterrupt:
            producer.disconnect()
            exit(0)

    producer.disconnect()