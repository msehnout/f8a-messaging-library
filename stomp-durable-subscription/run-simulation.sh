#!/bin/bash

if uname -a | grep Darwin;
then
	TIMEOUT='gtimeout'
else
	TIMEOUT='timeout'
fi

echo "# Running the subscription for the first time"
echo "# 1st durable subscription"
${TIMEOUT} 1 python3 stomp-recv.py
echo "# 2nd durable subscription"
${TIMEOUT} 1 python3 stomp-recv2.py

for i in $(seq 1 10);
do
	echo "# sending hello ${i}"
	bash stomp-send.sh "hello ${i}"
done

echo "# Running the subscription for the second time"
echo "# 1st durable subscription"
${TIMEOUT} 2 python3 stomp-recv.py
echo "# 2nd durable subscription"
${TIMEOUT} 2 python3 stomp-recv2.py
