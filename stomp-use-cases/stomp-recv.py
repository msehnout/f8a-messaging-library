import time
import stomp


class MyListener(stomp.ConnectionListener):

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print('received a message "%s"' % message)


hosts = [('localhost', 61613)]

conn = stomp.Connection(host_and_ports=hosts)
conn.set_listener('', MyListener())
conn.start()
conn.connect('admin', 'admin', wait=True, headers={'client-id': 'clientname'})
conn.subscribe(destination='/topic/test',
               id=1,
               ack='auto',
               headers={
                   'subscription-type': 'MULTICAST',
                   'durable-subscription-name':'someValue'}
               )

time.sleep(20)
conn.disconnect()
