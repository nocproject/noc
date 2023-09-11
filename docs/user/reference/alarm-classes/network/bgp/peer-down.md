---
uuid: 1b01710e-b3e7-4ff5-b718-2b6925bc6537
---
# Network | BGP | Peer Down

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
peer | BGP Peer | {{ no }}
vrf | VRF | {{ no }}
reason | Reason | {{ no }}
as | BGP Peer AS | `=PeerDS.remote_asn`
local_as | Local AS | `=PeerDS.local_asn`
description | BGP Peer Description | `=PeerDS.description`
import_filter | BGP Import Filter | `=PeerDS.import_filter`
export_filter | BGP Export Filter | `=PeerDS.export_filter`

## Events

### Opening Events
`Network | BGP | Peer Down` may be raised by events

Event Class | Description
--- | ---
[Network \| BGP \| Peer Down](../../../event-classes/network/bgp/peer-down.md) | dispose
[Network \| BGP \| Backward Transition](../../../event-classes/network/bgp/backward-transition.md) | dispose
[Network \| BGP \| Peer State Changed](../../../event-classes/network/bgp/peer-state-changed.md) | raise

### Closing Events
`Network | BGP | Peer Down` may be cleared by events

Event Class | Description
--- | ---
[Network \| BGP \| Established](../../../event-classes/network/bgp/established.md) | dispose
[Network \| BGP \| Peer State Changed](../../../event-classes/network/bgp/peer-state-changed.md) | clear_peer_down
