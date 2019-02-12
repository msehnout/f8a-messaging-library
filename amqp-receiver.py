import sys

from proton.handlers import MessagingHandler
from proton.reactor import Container, DurableSubscription


class ReceiveHandler(MessagingHandler):
    def __init__(self, conn_url, address, dur_id):
        super(ReceiveHandler, self).__init__()

        self.conn_url = conn_url
        self.address = address
        self.desired = 0
        self.dur_id = dur_id
        self.received = 0

    def on_start(self, event):
        if self.dur_id is not None:
            durable = DurableSubscription()
            event.container.container_id = self.dur_id
            conn = event.container.connect(self.conn_url)
            event.container.create_receiver(
                conn,
                self.address,
                name=self.dur_id,
                options=durable
            )
        else:
            conn = event.container.connect(self.conn_url)
            event.container.create_receiver(conn, self.address)

    def on_link_opened(self, event):
        print("RECEIVE: Created receiver for source address '{0}'".format
              (self.address))

    def on_message(self, event):
        message = event.message

        print("RECEIVE: Received message '{0}'".format(message.body))

        self.received += 1

        if self.received == self.desired:
            if self.dur_id is not None:
                event.receiver.detach()
            else:
                event.receiver.close()
            event.connection.close()

def main():
    try:
        conn_url, address = sys.argv[1:3]
    except ValueError:
        sys.exit("Usage: receive.py <connection-url> <address> [<durable-subscription-id>]")

    try:
        dur_id = sys.argv[3]
        print("Using durable connection ID: " + dur_id)
    except (IndexError, ValueError):
        dur_id = None

    handler = ReceiveHandler(conn_url, address, dur_id)
    container = Container(handler)
    container.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass