import optparse
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

class Send(MessagingHandler):
    def __init__(self, url, messages):
        super(Send, self).__init__()
        self.url = url
        self.sent = 0
        self.confirmed = 0
        self.total = messages

    def on_start(self, event):
        event.container.create_sender(self.url)

    def on_sendable(self, event):
        while event.sender.credit and self.sent < self.total:
            msg = Message(id=(self.sent + 1),
                    body={'sequence': (self.sent + 1)})
            event.sender.send(msg)
            self.sent += 1

    def on_accepted(self, event):
        self.confirmed += 1
        if self.confirmed == self.total:
            print("all messages confirmed")
            event.connection.close()

    def on_disconnected(self, event):
        self.sent = self.confirmed

parser = optparse.OptionParser(
        usage="usage: %prog [options]",
        description="Send messages to the supplied address.")

parser.add_option(
        "-a", "--address",
        default="topic://localhost:5672/examples",
        help="address to which messages are sent (default %default)")

parser.add_option(
        "-m", "--messages", type="int", default=100,
        help="number of messages to send (default %default)")

opts, args = parser.parse_args()

try:
    Container(Send(opts.address, opts.messages)).run()
except KeyboardInterrupt:
    pass
