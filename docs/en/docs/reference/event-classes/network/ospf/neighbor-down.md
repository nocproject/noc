---
uuid: a148d17b-feab-42ba-86c5-f83edc494495
---
# Network | OSPF | Neighbor Down

OSPF adjacency down

## Symptoms

Routing table changes and possible lost of connectivity

## Probable Causes

Link failure or protocol misconfiguration

## Recommended Actions

Check links and local and neighbor router configuration

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

### Raising alarms

`Network | OSPF | Neighbor Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| OSPF \| Neighbor Down](../../../alarm-classes/network/ospf/neighbor-down.md) | dispose
