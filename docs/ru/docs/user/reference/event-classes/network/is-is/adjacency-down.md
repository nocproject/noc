---
uuid: 87e5b0e2-43de-4983-99fc-0af4029ff305
---
# Network | IS-IS | Adjacency Down

IS-IS adjacency down

## Symptoms

Routing table changes and possible lost of connectivity

## Probable Causes

ISIS successfully established adjacency with neighbor

## Recommended Actions

Check links and local and neighbor's router configuration

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
neighbor | str | {{ yes }} | Neighbor's NSAP or name
interface | interface_name | {{ yes }} | Interface
level | str | {{ no }} | Level
reason | str | {{ no }} | Adjacency lost reason

## Alarms

### Raising alarms

`Network | IS-IS | Adjacency Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| IS-IS \| Adjacency Down](../../../alarm-classes/network/is-is/adjacency-down.md) | dispose
