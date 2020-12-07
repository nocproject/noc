---
uuid: eeffb1d4-7ce3-4967-917c-fd8cdd949a23
---
# Network | BGP | Peer Down

BGP Peer Down

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer
vrf | str | {{ no }} | VRF
as | int | {{ no }} | Peer AS
reason | str | {{ no }} | Reason

## Alarms

### Raising alarms

`Network | BGP | Peer Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| BGP \| Peer Down](../../../alarm-classes/network/bgp/peer-down.md) | dispose
