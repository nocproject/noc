---
uuid: 34f10707-7cf1-4e15-8262-47c4e25954d6
---
# Network | RSVP | Neighbor Down

RSVP Neighbor down

## Symptoms

Routing table changes and possible lost of connectivity

## Probable Causes

RSVP protocol configuration problem or link failure

## Recommended Actions

Check links and local and neighbor's router configuration

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
neighbor | ip_address | {{ yes }} | Neighbor's NSAP or name
reason | str | {{ no }} | Reason

## Alarms

### Raising alarms

`Network | RSVP | Neighbor Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| RSVP \| Neighbor Down](../../../alarm-classes/network/rsvp/neighbor-down.md) | dispose
