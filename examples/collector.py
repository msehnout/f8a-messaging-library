import mb
import time
import logging
import os

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)


time.sleep(20)
consumer = mb.MbConsumer([mb.TOPIC_RELEASE_MONITORING_NPM, mb.TOPIC_RELEASE_MONITORING_PYPI])
statistics = {"npm-updates": 0, "pypi-updates": 0}
while True:
    try:
        msg = consumer.next_message()
        if msg.path == mb.TOPIC_RELEASE_MONITORING_PYPI.path:
            statistics["pypi-updates"] += 1
            logger.info("Report: Detected {} PYPI updates".format(statistics["pypi-updates"]))
        else:
            statistics["npm-updates"] += 1
            logger.info("Report: Detected {} NPM updates".format(statistics["npm-updates"]))
        consumer.ack_message(msg)
    except KeyboardInterrupt:
        consumer.disconnect()
        exit(0)
