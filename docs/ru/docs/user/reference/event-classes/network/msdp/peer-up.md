---
uuid: 2175cc38-9d47-4351-8b17-3a601e59b5e9
---
# Network | MSDP | Peer Up

MSDP peer up

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer's IP
vrf | str | {{ no }} | VRF

## Alarms

### Clearing alarms

`Network | MSDP | Peer Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| MSDP \| Peer Down](../../../alarm-classes/network/msdp/peer-down.md) | dispose
