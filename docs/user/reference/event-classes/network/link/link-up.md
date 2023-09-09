---
uuid: 82d72502-974a-4c42-8fe4-c4d2aae71d5c
---
# Network | Link | Link Up

Link Up

## Symptoms

Connection restored

## Probable Causes

Administrative action, cable or hardware replacement

## Recommended Actions

Check interfaces on both sides for possible errors

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Affected interface
speed | str | {{ no }} | Link speed
duplex | str | {{ no }} | Duplex mode

## Alarms

### Clearing alarms

`Network | Link | Link Up` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| Link \| Link Down](../../../alarm-classes/network/link/link-down.md) | Clear Link Down
[Network \| Link \| Err-Disable](../../../alarm-classes/network/link/err-disable.md) | Clear Err-Disable
[Network \| STP \| BPDU Guard Violation](../../../alarm-classes/network/stp/bpdu-guard-violation.md) | Clear BPDU Guard Violation
[Network \| STP \| Root Guard Violation](../../../alarm-classes/network/stp/root-guard-violation.md) | Clear Root Guard Violation
