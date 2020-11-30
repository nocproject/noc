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
