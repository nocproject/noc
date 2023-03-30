---
uuid: f95dcd42-a73f-45ea-8e68-8d03347942a7
---
# Network | PIM | MSDP Peer Down

MSDP peer down

## Symptoms

Multicast flows lost

## Probable Causes

MSDP protocol configuration problem or link failure

## Recommended Actions

Check links and local and neighbor's router configuration

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer's IP
vrf | str | {{ no }} | VRF
reason | str | {{ no }} | Reason

## Alarms

### Raising alarms

`Network | PIM | MSDP Peer Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| PIM \| MSDP Peer Down](../../../alarm-classes/network/pim/msdp-peer-down.md) | dispose
