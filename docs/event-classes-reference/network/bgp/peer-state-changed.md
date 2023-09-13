---
uuid: b4ab69c1-15d3-4dd9-a6c8-aecb25c249b0
---
# Network | BGP | Peer State Changed

BGP Peer State Changed

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer
vrf | str | {{ no }} | VRF
as | int | {{ no }} | Peer AS
from_state | str | {{ no }} | Initial state
to_state | str | {{ no }} | Final state

## Alarms

### Raising alarms

`Network | BGP | Peer State Changed` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| BGP \| Peer Down](../../../alarm-classes/network/bgp/peer-down.md) | raise

### Clearing alarms

`Network | BGP | Peer State Changed` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| BGP \| Peer Down](../../../alarm-classes/network/bgp/peer-down.md) | clear_peer_down
[Network \| BGP \| Prefix Limit Exceeded](../../../alarm-classes/network/bgp/prefix-limit-exceeded.md) | clear_maxprefix
