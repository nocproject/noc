---
uuid: 81215d7f-71b8-491e-8492-7e5734660eb1
---
# Network | MAC | Duplicate MAC

Duplicate MAC detected

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ yes }} | MAC Address
one_interface | interface_name | {{ yes }} | First interface
two_interface | interface_name | {{ yes }} | Second interface

## Alarms

### Raising alarms

`Network | MAC | Duplicate MAC` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| MAC \| Duplicate MAC](../../../alarm-classes/network/mac/duplicate-mac.md) | dispose
