---
uuid: bd8fa1b4-9bd9-4bef-a557-756255ccad1e
---
# Network | PIM | DR Change

## Symptoms

Some multicast flows lost

## Probable Causes

Link failure or protocol misconfiguration

## Recommended Actions

Check links and local and neighbor router configuration

## Variables

Variable | Description | Default
--- | --- | ---
interface | Interface | {{ no }}
from_dr | From DR | {{ no }}
to_dr | To DR | {{ no }}
vrf | VRF | {{ no }}

## Events

### Opening Events
`Network | PIM | DR Change` may be raised by events

Event Class | Description
--- | ---
[Network \| PIM \| DR Change](../../../event-classes/network/pim/dr-change.md) | dispose
