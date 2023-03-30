---
uuid: cba69e5c-275b-4d39-a773-bd210802f86a
---
# Network | RSVP | Neighbor Up

RSVP Neighbor up

## Symptoms

Routing table changes

## Probable Causes

RSVP successfully established Neighbor with neighbor

## Recommended Actions

No reaction needed

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
neighbor | ip_address | {{ yes }} | Neighbor's NSAP or name

## Alarms

### Clearing alarms

`Network | RSVP | Neighbor Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| RSVP \| Neighbor Down](../../../alarm-classes/network/rsvp/neighbor-down.md) | dispose
