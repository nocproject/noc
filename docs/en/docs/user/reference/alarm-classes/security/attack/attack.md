---
uuid: b1187763-a252-491f-8683-d791a09ae95f
---
# Security | Attack | Attack

## Symptoms

Unsolicitized traffic from source

## Probable Causes

Virus/Botnet activity or malicious actions

## Recommended Actions

Negotiate the source if it is your customer, or ignore

## Variables

Variable | Description | Default
--- | --- | ---
name | Attack name | {{ no }}
interface | Interface | {{ no }}
src_ip | Source IP | {{ no }}
src_mac | Source MAC | {{ no }}
vlan | Vlan ID | {{ no }}
description | Interface description | `=InterfaceDS.description`
vlan_name | Vlan name | `=VCDS.name`

## Events

### Opening Events
`Security | Attack | Attack` may be raised by events

Event Class | Description
--- | ---
[Security \| Attack \| Attack](../../../event-classes/security/attack/attack.md) | dispose
