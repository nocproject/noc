---
uuid: 4841c76c-8b00-4a70-bfd0-adafc80800f4
---
# Network | STP | STP Vlan Loop Detected

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
interface | interface | {{ no }}
vlan | vlan | {{ no }}
description | Interface description | `=InterfaceDS.description`
vlan_name | Vlan name | `=VCDS.name`
vlan_description | Vlan description | `=VCDS.description`
vlan_vc_domain | VC domain | `=VCDS.vc_domain`

## Events

### Opening Events
`Network | STP | STP Vlan Loop Detected` may be raised by events

Event Class | Description
--- | ---
[Network \| STP \| STP Vlan Loop Detected](../../../event-classes/network/stp/stp-vlan-loop-detected.md) | dispose

### Closing Events
`Network | STP | STP Vlan Loop Detected` may be cleared by events

Event Class | Description
--- | ---
[Network \| STP \| STP Vlan Loop Cleared](../../../event-classes/network/stp/stp-vlan-loop-cleared.md) | dispose
