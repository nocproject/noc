---
uuid: 9f18d201-55fd-4020-b32f-94532bb8e2cb
---
# Network | PIM | MSDP Peer Up

MSDP peer up

## Symptoms

Multicast flows send successfully

## Probable Causes

MSDP successfully established connect with peer

## Recommended Actions

No reaction needed

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer's IP
vrf | str | {{ no }} | VRF

## Alarms

### Clearing alarms

`Network | PIM | MSDP Peer Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| PIM \| MSDP Peer Down](../../../alarm-classes/network/pim/msdp-peer-down.md) | dispose
