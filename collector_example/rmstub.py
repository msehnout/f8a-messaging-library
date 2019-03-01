import mb
import time


time.sleep(5)
print("stub I")
topic_name = "release-monitoring"
producer = mb.MbProducer(mb.MbChannelType.TOPIC, topic_name)
print("stub II")
while True:
    try:
        msg = '{ "foo": "bar" }'
        producer.publish(msg)
        print("Publishing ...")
        time.sleep(5)
    except KeyboardInterrupt:
        producer.disconnect()
        exit(0)
