---
uuid: dcb43df5-cca3-4945-b3f1-b7d4140fdb4e
---
# Security | Attack | Attack

Attack in progress detected

## Symptoms

Unsolicitized traffic from source

## Probable Causes

Virus/Botnet activity or malicious actions

## Recommended Actions

Negotiate the source if it is your customer, or ignore

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
name | str | {{ yes }} | Attack name
interface | interface_name | {{ no }} | Interface
src_ip | ip_address | {{ no }} | Source IP
src_mac | mac | {{ no }} | Source MAC
vlan | int | {{ no }} | Vlan ID

## Alarms

### Raising alarms

`Security | Attack | Attack` events may raise following alarms:

Alarm Class | Description
--- | ---
[Security \| Attack \| Attack](../../../alarm-classes/security/attack/attack.md) | dispose
