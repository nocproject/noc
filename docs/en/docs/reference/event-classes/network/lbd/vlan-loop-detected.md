---
uuid: 654c492d-cb7f-46ce-b948-f4f8c718c36d
---
# Network | LBD | Vlan Loop Detected

LBD Vlan Loop Detected

## Symptoms

Connection lost on a specific vlan

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | LBD interface
vlan | int | {{ yes }} | Vlan

## Alarms

### Raising alarms

`Network | LBD | Vlan Loop Detected` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| LBD \| Vlan Loop Detected](../../../alarm-classes/network/lbd/vlan-loop-detected.md) | dispose
