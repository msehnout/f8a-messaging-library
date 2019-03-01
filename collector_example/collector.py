import mb
import time


time.sleep(4)
print("collector I")
topic_name = "release-monitoring"
consumer = mb.MbConsumer(mb.MbChannelType.TOPIC, topic_name)
statistics = {"npm-updates": 0}
print("collector II")
while True:
    try:
        consumer.next_message()
        statistics["npm-updates"] += 1
        print("Report: Detected {} NPM updates".format(statistics["npm-updates"]))
    except KeyboardInterrupt:
        consumer.disconnect()
        exit(0)
