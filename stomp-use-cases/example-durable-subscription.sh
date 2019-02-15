#!/bin/bash

if uname -a | grep Darwin;
then
	TIMEOUT='gtimeout'
else
	TIMEOUT='timeout'
fi

echo "# Running the subscription for the first time"
echo "# 1st durable subscription"
${TIMEOUT} 3 python3 stomp-recv.py
echo "# 2nd durable subscription"
${TIMEOUT} 3 python3 stomp-recv2.py

sleep 1

for i in $(seq 1 10);
do
	echo "# sending hello ${i}"
	bash stomp-send.sh "hello ${i}"
done

sleep 1

echo "# Running the subscription for the second time"
echo "# 1st durable subscription"
${TIMEOUT} 5 python3 stomp-recv.py
echo "# 2nd durable subscription"
${TIMEOUT} 5 python3 stomp-recv2.py
