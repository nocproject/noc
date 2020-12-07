---
uuid: 188f5509-7498-4039-a4e3-41eb5d504585
---
# Network | MPLS | LDP Neighbor Down

MPLS LDP Neighbor Down

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
neighbor | ip_address | {{ yes }} | LDP Neighbor
state | str | {{ no }} | state
reason | str | {{ no }} | Reason

## Alarms

### Raising alarms

`Network | MPLS | LDP Neighbor Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| MPLS \| LDP Neighbor Down](../../../alarm-classes/network/mpls/ldp-neighbor-down.md) | dispose
