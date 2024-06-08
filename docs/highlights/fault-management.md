# Fault Management

Fault Management is the process of collecting and processing
incoming events, coming from various sources. NOC provides flexible
event processing pipeline split to cleanly separated stages:

* _Collection_ - Collecting events from external sources, like Syslog, SNMP Trap, active probes,
metrics thresholds and injecting them into event processing pipeline.
* _Classification_ - removing of all device-depended personality and
replacing them by generalized [Event Classes](../concepts/event-class/index.md).
NOC recognizes about 300 event classes out of the box.
* _Correlation_ - Analysis of possible alarm opening and closing events, rule-based correlation,
topology-based correlation, raising and clearing of alarms, calculation of service impact
* _Escalation_ - Rule-based alarm processing, notification and escalation
to external trouble ticket systems.

Each stage processing by different set of [microservices](microservices.md),
allowing to adjust amount of workers according your actual workload. Multi-stage
processing allows to focus monitoring staff to fix only actual problems
which causes service degradation.

## See Also

* [Fault Management](../fault-management/index.md)