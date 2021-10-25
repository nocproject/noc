# Managed Object

`Managed Object` is a core concept for NOC. Shortly it is the entity
which can be _managed_ by NOC by any means as actively (via CLI, SNMP or HTTP)
or passively (SYSLOG, SNMP Traps, Netflow)

## Group Settings

Group settings for Managed Object are contained in [Managed Object Profile](../managed-object-profile/index.md)

## Divisions

Managed Object is participating in several independentent _divisions_, each
answering particular question:

- **Administrative:** _Who is responsible for object?_
  See [Administrative Domain](../administrative-domain/index.md)
- **Network Segment:** _What position in network hierarchy object holds?_
  See [Network Segment](../network-segment/index.md)
- **Container:** _Where object is located?_
  See [Container](../container/index.md)

Managed Object must belong to only one division of particular type

## Uplinks

Except in rare cases _Managed Objects_ should have one or more _Paths_
to upper levels of network (to establish _Connectivity_ with all network)
or to the NOC's probes (to be monitored and managed at all).

Those paths are called _Uplink Paths_ and all direct _Neighbors_ on the
_Uplink Paths_ are called _Uplinks_. The role of _Uplink_ is to provide
_Connectivity_ for its _Downlink_. For reserved topologies object's _Uplink_ may be
its _Downlink_ at the same time.

_Uplinks_ are key concept for [RCA](../../../../glossary.md#rca). _Managed Object_ with all unavailable
uplinks looses _Connectivity_ and problem lies somewhere on the _Uplink Paths_.

NOC perform automatic uplinks calculation on topology changes. The proccess
can be configured via [Network Segment Profiles](../network-segment-profile/index.md)
[Uplink Policy](../network-segment-profile/index.md#uplink-policy) setting.
