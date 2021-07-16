---
uuid: 66a6a42d-8511-47b5-a738-f28ff359cc6d
---
# Network | MAC | Invalid MAC

Invalid MAC detected

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ yes }} | MAC Address
interface | interface_name | {{ yes }} | Affected interface
vlan | int | {{ no }} | Affected vlan

## Alarms

### Raising alarms

`Network | MAC | Invalid MAC` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| MAC \| Invalid MAC](../../../alarm-classes/network/mac/invalid-mac.md) | dispose
