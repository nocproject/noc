---
uuid: 132e470f-6dae-4e85-915f-d861934a56ab
---
# Network | BGP | Established

BGP Session Established

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer
vrf | str | {{ no }} | VRF
as | int | {{ no }} | Peer AS

## Alarms

### Clearing alarms

`Network | BGP | Established` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| BGP \| Peer Down](../../../alarm-classes/network/bgp/peer-down.md) | dispose
[Network \| BGP \| Prefix Limit Exceeded](../../../alarm-classes/network/bgp/prefix-limit-exceeded.md) | dispose
