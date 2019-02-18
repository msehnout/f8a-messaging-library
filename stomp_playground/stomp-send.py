import stomp

conn = stomp.Connection()
conn.start()
conn.connect('admin', 'password', wait=True)
conn.send(body='ahoj', destination='/topic/test')
conn.disconnect()
