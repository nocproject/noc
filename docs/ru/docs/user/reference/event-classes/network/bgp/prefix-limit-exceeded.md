---
uuid: d028a97e-8501-4633-a043-09c0f25819bd
---
# Network | BGP | Prefix Limit Exceeded

BGP Prefix Limit Exceeded

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

### Raising alarms

`Network | BGP | Prefix Limit Exceeded` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| BGP \| Prefix Limit Exceeded](../../../alarm-classes/network/bgp/prefix-limit-exceeded.md) | dispose
