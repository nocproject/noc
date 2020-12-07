---
uuid: 2f065913-7e23-438e-8b2f-9ca613d25706
---
# Network | Storm Control | Unicast Storm Detected

## Symptoms

## Probable Causes

## Recommended Actions

Enable DLF (destination lookup failure) filter

## Variables

Variable | Description | Default
--- | --- | ---
interface | interface | {{ no }}
description | Interface description | `=InterfaceDS.description`

## Events

### Opening Events
`Network | Storm Control | Unicast Storm Detected` may be raised by events

Event Class | Description
--- | ---
[Network \| Storm Control \| Unicast Storm Detected](../../../event-classes/network/storm-control/unicast-storm-detected.md) | dispose

### Closing Events
`Network | Storm Control | Unicast Storm Detected` may be cleared by events

Event Class | Description
--- | ---
[Network \| Storm Control \| Unicast Storm Cleared](../../../event-classes/network/storm-control/unicast-storm-cleared.md) | dispose
