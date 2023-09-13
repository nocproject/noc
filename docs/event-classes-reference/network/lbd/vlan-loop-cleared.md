---
uuid: 47a0fb97-5b04-406d-bc27-4f31c1df8399
---
# Network | LBD | Vlan Loop Cleared

LBD Vlan Loop Cleared

## Symptoms

Connection restore on a specific vlan

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | LBD interface
vlan | int | {{ yes }} | Vlan

## Alarms

### Clearing alarms

`Network | LBD | Vlan Loop Cleared` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| LBD \| Vlan Loop Detected](../../../alarm-classes/network/lbd/vlan-loop-detected.md) | dispose
