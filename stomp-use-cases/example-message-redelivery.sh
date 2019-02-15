#!/bin/bash

if uname -a | grep Darwin;
then
	TIMEOUT='gtimeout'
else
	TIMEOUT='timeout'
fi

echo "# Running the subscription for the first time"
echo "# Subscribe!"
python3 stomp-recv-ack.py &
RECV_PID=$!

sleep 3

for i in $(seq 1 5);
do
	MSG="ack these!"
	echo "# sending ${MSG} ${i}"
	bash stomp-send.sh "hello ${MSG} ${i}"
done

sleep 4

for i in $(seq 1 3);
do
	MSG="don't ack these yet!"
	echo "# sending ${MSG} ${i}"
	bash stomp-send.sh "hello ${MSG} ${i}"
done

sleep 2

echo "# Killing the consumer"
kill $RECV_PID

sleep 2

echo "# Running it again"
echo "# You should see the last 3 messages once again. This time wait for the process to ACK them."
${TIMEOUT} 8 python3 stomp-recv-ack.py

echo "# Running it for the last time"
echo "# Now you should not see any new messages"
${TIMEOUT} 3 python3 stomp-recv-ack.py
