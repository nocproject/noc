---
uuid: c3a089e3-16b8-42aa-a4d2-801049177a22
---
# Network | LBD | Vlan Loop Detected

## Symptoms

Lost traffic on specific vlan

## Probable Causes

## Recommended Actions

Check topology or use STP to avoid loops

## Variables

Variable | Description | Default
--- | --- | ---
interface | interface | {{ no }}
vlan | Vlan | {{ no }}
description | Interface description | `=InterfaceDS.description`
vlan_name | Vlan name | `=VCDS.name`
vlan_description | Vlan description | `=VCDS.description`
vlan_vc_domain | VC domain | `=VCDS.vc_domain`

## Events

### Opening Events
`Network | LBD | Vlan Loop Detected` may be raised by events

Event Class | Description
--- | ---
[Network \| LBD \| Vlan Loop Detected](../../../event-classes/network/lbd/vlan-loop-detected.md) | dispose

### Closing Events
`Network | LBD | Vlan Loop Detected` may be cleared by events

Event Class | Description
--- | ---
[Network \| LBD \| Vlan Loop Cleared](../../../event-classes/network/lbd/vlan-loop-cleared.md) | dispose
