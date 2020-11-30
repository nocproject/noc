---
uuid: c2b490f2-a0e2-4d44-8e1b-080eb7137835
---
# Network | PIM | Invalid RP

## Symptoms

## Probable Causes

A PIM router received a register message from another PIM router that identifies itself as the rendezvous point. If the router is not configured for another rendezvous point, it will not accept the register message.

## Recommended Actions

Configure all leaf routers (first-hop routers to multicast sources) with the IP address of the valid rendezvous point.

## Variables

Variable | Description | Default
--- | --- | ---
pim_router | PIM router IP | {{ no }}
invalid_rp | Invalid RP IP | {{ no }}

## Events

### Opening Events
`Network | PIM | Invalid RP` may be raised by events

Event Class | Description
--- | ---
[Network \| PIM \| Invalid RP](../../../event-classes/network/pim/invalid-rp.md) | dispose
