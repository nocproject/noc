---
uuid: 951053ed-a46f-41aa-ae4b-05931c63d425
---
# Network | IMPB | Unauthenticated IP-MAC

## Symptoms

Discard user connection attempts

## Probable Causes

## Recommended Actions

Check user IP and MAC, check IMPB entry, check topology

## Variables

Variable | Description | Default
--- | --- | ---
ip | User IP | {{ no }}
mac | User MAC | {{ no }}
interface | Affected interface | {{ no }}
description | Interface description | `=InterfaceDS.description`

## Events

### Opening Events
`Network | IMPB | Unauthenticated IP-MAC` may be raised by events

Event Class | Description
--- | ---
[Network \| IMPB \| Unauthenticated IP-MAC](../../../event-classes/network/impb/unauthenticated-ip-mac.md) | dispose

### Closing Events
`Network | IMPB | Unauthenticated IP-MAC` may be cleared by events

Event Class | Description
--- | ---
[Network \| IMPB \| Recover IMPB stop learning state](../../../event-classes/network/impb/recover-impb-stop-learning-state.md) | dispose
