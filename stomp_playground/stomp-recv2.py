import time
import sys

import stomp

class MyListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('received an error "%s"' % message)
    def on_message(self, headers, message):
        print('received a message "%s"' % message)
hosts = [('localhost', 61613)]

conn = stomp.Connection(host_and_ports=hosts)
conn.start()
conn.connect('admin', 'admin', wait=True,headers = {'client-id': 'clientname'} )
conn.set_listener('', MyListener())
conn.subscribe(destination='/topic/test', id=1, ack='auto',headers = {'subscription-type': 'MULTICAST','durable-subscription-name':'someValue2'})
#conn.subscribe({destination=config['/topic/test'], ack:'auto', 'activemq.subscriptionName':'SampleSubscription'})
#conn.subscribe(destination='/topic/testTopic', ack='auto', headers = {'activemq.subscriptionName': 'myhostname'})

#conn.send(body=' '.join(sys.argv[1:]), destination='/topic/test')

time.sleep(20)
conn.disconnect()
