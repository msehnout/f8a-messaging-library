```
docker run -p 8161:8161 -p 5671:5671 -p 5672:5672 -p 61613:61613 -e AMQ_USER=user -e AMQ_PASSWORD=redhat -e AMQ_PROTOCOL=amqp,stomp -e AMQ_QUEUES=foo -e AMQ_ADDRESSES=bar -e ADMIN_PASSWORD=redhat registry.access.redhat.com/amq-broker-7/amq-broker-72-openshift
qb message receive  -b 127.0.0.1:5672 -c 10 topic://amq.topic/example
qb message send -b 127.0.0.1:5672 topic://amq.topic/example ahoj
```
