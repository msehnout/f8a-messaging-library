#!/bin/bash

HOST="localhost"
PORT="61613"
LOGIN="admin"
PASSCODE="password"
CHANNEL="test"
MSG="$1"

echo -en "CONNECT

login:${LOGIN}
passcode:${PASSCODE}

\x00


SEND
destination:/topic/${CHANNEL}

${MSG}\x00
" | nc $HOST $PORT
