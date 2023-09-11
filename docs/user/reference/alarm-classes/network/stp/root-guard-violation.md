---
uuid: ca261ef8-3d29-4270-8fd2-eb616d9e6e76
---
# Network | STP | Root Guard Violation

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
`Network | STP | Root Guard Violation` may be raised by events

Event Class | Description
--- | ---
[Network \| STP \| BPDU Root Violation](../../../event-classes/network/stp/bpdu-root-violation.md) | dispose

### Closing Events
`Network | STP | Root Guard Violation` may be cleared by events

Event Class | Description
--- | ---
[Network \| STP \| Root Guard Recovery](../../../event-classes/network/stp/root-guard-recovery.md) | dispose
[Network \| Link \| Link Up](../../../event-classes/network/link/link-up.md) | Clear Root Guard Violation
