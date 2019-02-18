import time
import sys

import stomp

last_id = 0


class MyListener(stomp.ConnectionListener):

    def on_error(self, headers, message):
        print(headers)
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        global last_id
        last_id = headers['message-id']
        print('received a message "%s"' % message)


hosts = [('localhost', 61613)]

conn = stomp.Connection(host_and_ports=hosts)
conn.set_listener('', MyListener())
conn.start()
conn.connect('admin', 'admin', wait=True,headers={'client-id': 'clientname'})
conn.subscribe(destination='/topic/test',
               id='1',
               ack='client',
               headers={
                   'subscription-type': 'MULTICAST',
                   'durable-subscription-name': 'someValue'
               })

while True:
    try:
        time.sleep(5)
        conn.ack(str(last_id), '1')
        print("ACK")
    except KeyboardInterrupt:
        conn.disconnect()
        print("Bye, bye!")
        sys.exit(0)
