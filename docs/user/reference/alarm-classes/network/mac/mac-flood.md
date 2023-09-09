---
uuid: b761d498-a29f-41e0-9e8d-20ce696394a2
---
# Network | MAC | MAC Flood

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
mac | MAC Address | {{ no }}
vlan | VLAN | {{ no }}
interface | Interface | {{ no }}
vlan_name | Vlan name | `=VCDS.name`
vlan_description | Vlan description | `=VCDS.description`
vlan_vc_domain | VC domain | `=VCDS.vc_domain`

## Events

### Opening Events
`Network | MAC | MAC Flood` may be raised by events

Event Class | Description
--- | ---
[Network \| MAC \| MAC Flood](../../../event-classes/network/mac/mac-flood.md) | dispose
