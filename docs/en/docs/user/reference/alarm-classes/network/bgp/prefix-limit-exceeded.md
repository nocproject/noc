---
uuid: 8a0ffe77-c3c0-4327-b52b-7b482e710aec
---
# Network | BGP | Prefix Limit Exceeded

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
peer | BGP Peer | {{ no }}
vrf | VRF | {{ no }}
as | BGP Peer AS | {{ no }}

## Events

### Opening Events
`Network | BGP | Prefix Limit Exceeded` may be raised by events

Event Class | Description
--- | ---
[Network \| BGP \| Prefix Limit Exceeded](../../../event-classes/network/bgp/prefix-limit-exceeded.md) | dispose

### Closing Events
`Network | BGP | Prefix Limit Exceeded` may be cleared by events

Event Class | Description
--- | ---
[Network \| BGP \| Established](../../../event-classes/network/bgp/established.md) | dispose
[Network \| BGP \| Peer State Changed](../../../event-classes/network/bgp/peer-state-changed.md) | clear_maxprefix
