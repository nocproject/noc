---
uuid: 68e8e127-e30a-4eb5-8e4f-b16621f96e7a
---
# Network | MSDP | Peer Down

MSDP peer down

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer's IP
vrf | str | {{ no }} | VRF
reason | str | {{ no }} | Reason

## Alarms

### Raising alarms

`Network | MSDP | Peer Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| MSDP \| Peer Down](../../../alarm-classes/network/msdp/peer-down.md) | dispose
