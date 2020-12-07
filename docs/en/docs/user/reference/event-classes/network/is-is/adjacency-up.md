---
uuid: a4af4dd8-4139-4577-85e6-236d85e4d838
---
# Network | IS-IS | Adjacency Up

ISIS adjacency up

## Symptoms

Routing table changes

## Probable Causes

IS-IS successfully established adjacency with neighbor

## Recommended Actions

No reaction needed

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
neighbor | str | {{ yes }} | Neighbor's NSAP or name
interface | interface_name | {{ yes }} | Interface
level | str | {{ no }} | Level

## Alarms

### Clearing alarms

`Network | IS-IS | Adjacency Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| IS-IS \| Adjacency Down](../../../alarm-classes/network/is-is/adjacency-down.md) | dispose
