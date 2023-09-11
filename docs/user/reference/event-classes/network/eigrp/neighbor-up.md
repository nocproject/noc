---
uuid: ae8f0855-4d07-407d-9443-c29dee762288
---
# Network | EIGRP | Neighbor Up

EIGRP neighbor up

## Symptoms

Routing table changes

## Probable Causes

An EIGRP adjacency was established with the indicated neighboring router. The local router can now exchange information with it.

## Recommended Actions

No specific actions needed

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
as | str | {{ no }} | EIGRP autonomus system
interface | str | {{ yes }} | Interface
neighbor | ip_address | {{ yes }} | Neighbor's Router ID
reason | str | {{ no }} | Adjacency lost reason
to_state | str | {{ no }} | to state

## Alarms

### Clearing alarms

`Network | EIGRP | Neighbor Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| EIGRP \| Neighbor Down](../../../alarm-classes/network/eigrp/neighbor-down.md) | dispose
