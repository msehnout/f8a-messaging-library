import time
import stomp

from queue import Queue

q = Queue()


class _StompListener(stomp.ConnectionListener):
    """Implements listener needed to handle stomp events."""

    def __init__(self, queue):
        self.queue = queue

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        self.queue.put(message)


class MyListener(stomp.ConnectionListener):

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print('received a message "%s"' % message)


hosts = [('localhost', 61613)]

conn = stomp.Connection(host_and_ports=hosts)
#conn.set_listener('', MyListener())
#conn.start()
conn.connect('admin', 'admin', wait=True, headers={'client-id': 'clientname'})
conn.set_listener('', _StompListener(q))
conn.subscribe(destination='/topic/test',
               id=1,
               ack='auto',
               headers={
                   'subscription-type': 'MULTICAST',
                   'durable-subscription-name':'someValue'}
               )

while True:
    item = q.get()
    if item == "exit":
        break

    print(item)
    q.task_done()

conn.disconnect()
