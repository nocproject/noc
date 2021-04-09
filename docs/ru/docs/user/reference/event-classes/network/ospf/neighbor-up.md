---
uuid: f319d6f6-bd45-4e18-b232-45b270fd1c29
---
# Network | OSPF | Neighbor Up

OSPF neighbor up

## Symptoms

Routing table changes

## Probable Causes

An OSPF adjacency was established with the indicated neighboring router. The local router can now exchange information with it.

## Recommended Actions

No specific actions needed

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
area | str | {{ no }} | OSPF area
interface | interface_name | {{ yes }} | Interface
neighbor | ip_address | {{ yes }} | Neighbor's Router ID
reason | str | {{ no }} | Adjacency lost reason
from_state | str | {{ no }} | from state
to_state | str | {{ no }} | to state
vrf | str | {{ no }} | VRF

## Alarms

### Clearing alarms

`Network | OSPF | Neighbor Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| OSPF \| Neighbor Down](../../../alarm-classes/network/ospf/neighbor-down.md) | dispose
