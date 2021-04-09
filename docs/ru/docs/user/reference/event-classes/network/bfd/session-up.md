---
uuid: c81f31b9-f8a6-425a-a5b4-d4d3653f62f8
---
# Network | BFD | Session Up

BFD Session Up

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | BFD interface
peer | ip_address | {{ yes }} | BFD Peer

## Alarms

### Clearing alarms

`Network | BFD | Session Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| BFD \| Session Down](../../../alarm-classes/network/bfd/session-down.md) | dispose
