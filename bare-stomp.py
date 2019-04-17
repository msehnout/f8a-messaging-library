import time
import sys

import stomp


class MyListener(stomp.ConnectionListener):

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print('received a message "%s"' % message)


conn = stomp.Connection()
conn.set_listener('', MyListener())
conn.start()
conn.connect('admin', 'password', wait=True)

print('subscribe')
conn.subscribe(destination='/queue/Consumer.Foo.VirtualTopic.T', id='1', ack='auto')
time.sleep(1)

for i in range(1, 10):
    print('sending')
    conn.send(body='ahoj', destination='/topic/VirtualTopic.T')
    time.sleep(1)

conn.disconnect()