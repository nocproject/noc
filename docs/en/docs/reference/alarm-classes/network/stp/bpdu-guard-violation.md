---
uuid: 20d3c3e7-1c33-458d-9e12-837670bbd080
---
# Network | STP | BPDU Guard Violation

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
interface | interface | {{ no }}
description | Interface description | `=InterfaceDS.description`

## Events

### Opening Events
`Network | STP | BPDU Guard Violation` may be raised by events

Event Class | Description
--- | ---
[Network \| STP \| BPDU Guard Violation](../../../event-classes/network/stp/bpdu-guard-violation.md) | dispose

### Closing Events
`Network | STP | BPDU Guard Violation` may be cleared by events

Event Class | Description
--- | ---
[Network \| STP \| BPDU Guard Recovery](../../../event-classes/network/stp/bpdu-guard-recovery.md) | dispose
[Network \| Link \| Link Up](../../../event-classes/network/link/link-up.md) | Clear BPDU Guard Violation
