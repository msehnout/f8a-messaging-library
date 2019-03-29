import mb
import time
import logging
import os

logger = logging.getLogger(__file__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)


time.sleep(20)
logger.info("collector I")
topic_name = "release-monitoring"
consumer = mb.MbConsumer(mb.MbChannelType.TOPIC, topic_name)
statistics = {"npm-updates": 0}
logger.info("collector II")
while True:
    try:
        consumer.next_message()
        statistics["npm-updates"] += 1
        logger.info("Report: Detected {} NPM updates".format(statistics["npm-updates"]))
    except KeyboardInterrupt:
        consumer.disconnect()
        exit(0)
