---
uuid: 211d9e04-9595-465b-9257-7fd0d68ff10a
---
# Network | MAC | MAC Flap

## Symptoms

## Probable Causes

The system found the specified host moving between the specified ports.

## Recommended Actions

Examine the network for possible loops.

## Variables

Variable | Description | Default
--- | --- | ---
mac | MAC Address | {{ no }}
vlan | VLAN | {{ no }}
from_interface | From interface | {{ no }}
to_interface | To interface | {{ no }}
from_description | Interface description | `=fromInterfaceDS.description`
to_description | Interface description | `=toInterfaceDS.description`
vlan_name | Vlan name | `=VCDS.name`
vlan_description | Vlan description | `=VCDS.description`
vlan_vc_domain | VC domain | `=VCDS.vc_domain`

## Events

### Opening Events
`Network | MAC | MAC Flap` may be raised by events

Event Class | Description
--- | ---
[Network \| MAC \| MAC Flap](../../../event-classes/network/mac/mac-flap.md) | dispose
