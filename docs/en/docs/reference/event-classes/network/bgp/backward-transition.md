---
uuid: df53d877-2473-4074-a9a0-0a7352731784
---
# Network | BGP | Backward Transition

BGP Backward Transition

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer
vrf | str | {{ no }} | VRF
as | int | {{ no }} | Peer AS
state | str | {{ no }} | Transition from state

## Alarms

### Raising alarms

`Network | BGP | Backward Transition` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| BGP \| Peer Down](../../../alarm-classes/network/bgp/peer-down.md) | dispose
