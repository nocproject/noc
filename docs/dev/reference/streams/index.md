# Liftbridge Streams

Liftbridge streams are the one of ways of inter-process communications
inside NOC cluster.

## Events Pipeline
Main `Fault Management` pipeline. Events pipeline registers various events
either by active (pinging and probing) or by passive (various collectors)
means. Then, [classifier](../../../admin/reference/services/classifier.md) processes events, assigns them
[Event Classes](../../../user/reference/event-classes/index.md)
and detects events which may signal the raising or clearing alarm conditions.
Selected events are passed to [correlator](../../../admin/reference/services/correlator.md)
for further alarm state processing. 

```mermaid
graph LR
  ping -->|events.POOL| classifier
  syslogcollector -->|events.POOL| classifier
  trapcollector -->|events.POOL| classifier
  classifier -->|dispose.POOL| correlator
```

## Generic Message Exchange Pipeline
Generic Message Exchange Pipeline processes notifications of various system
events which may be delivered to outside system. Messages are sent
to [mx](../../../admin/reference/services/mx.md) service, which performs translation
and templating for messages and routes them to one of `*sender` services,
which perform delivery to outside endpoints.

```mermaid
graph LR
   System((System)) -->|mx| mx
   discovery -->|mx| mx
   datatream -->|mx| mx
   mx -->|kafkasender| kafkasender([kafkasender])
```
