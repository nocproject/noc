---
uuid: 99cdbce1-e7e8-42fd-99bc-a0091ffa6e3a
---
# Network | MPLS | LDP Neighbor Up

MPLS LDP Neighbor Up

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

### Clearing alarms

`Network | MPLS | LDP Neighbor Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| MPLS \| LDP Neighbor Down](../../../alarm-classes/network/mpls/ldp-neighbor-down.md) | dispose
