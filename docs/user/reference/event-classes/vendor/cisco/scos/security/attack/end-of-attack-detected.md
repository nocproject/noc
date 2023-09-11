---
uuid: 44947cd0-638a-4bdf-a1e8-5341249ea5eb
---
# Vendor | Cisco | SCOS | Security | Attack | End-of-attack detected

End-of-attack detected

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
from_ip | ip_address | {{ yes }} | From IP
to_ip | ip_address | {{ no }} | To IP
from_side | str | {{ yes }} | From Side
proto | str | {{ yes }} | Protocol
flows | int | {{ yes }} | Flows
duration | str | {{ yes }} | Duration
action | str | {{ yes }} | Action

## Alarms

### Clearing alarms

`Vendor | Cisco | SCOS | Security | Attack | End-of-attack detected` events may clear following alarms:

Alarm Class | Description
--- | ---
[Vendor \| Cisco \| SCOS \| Security \| Attack \| Attack Detected](../../../../../../alarm-classes/vendor/cisco/scos/security/attack/attack-detected.md) | Clear Attack Detected
