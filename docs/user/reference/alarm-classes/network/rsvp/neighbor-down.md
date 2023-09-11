---
uuid: a1086b80-e78b-4efe-b462-2ee0f2808a85
---
# Network | RSVP | Neighbor Down

## Symptoms

Routing table changes and possible lost of connectivity

## Probable Causes

Link failure or protocol misconfiguration

## Recommended Actions

Check links and local and neighbor router configuration

## Variables

Variable | Description | Default
--- | --- | ---
interface | Interface | {{ no }}
neighbor | Neighbor's NSAP or name | {{ no }}
reason | Neighbor lost reason | {{ no }}

## Events

### Opening Events
`Network | RSVP | Neighbor Down` may be raised by events

Event Class | Description
--- | ---
[Network \| RSVP \| Neighbor Down](../../../event-classes/network/rsvp/neighbor-down.md) | dispose

### Closing Events
`Network | RSVP | Neighbor Down` may be cleared by events

Event Class | Description
--- | ---
[Network \| RSVP \| Neighbor Up](../../../event-classes/network/rsvp/neighbor-up.md) | dispose
