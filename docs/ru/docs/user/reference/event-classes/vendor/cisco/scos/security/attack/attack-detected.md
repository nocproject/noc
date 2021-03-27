---
uuid: f80e3686-bd0c-4247-afcf-d79cf60cb832
---
# Vendor | Cisco | SCOS | Security | Attack | Attack Detected

Attack detected

## Symptoms

Possible DoS/DDoS traffic from source

## Probable Causes

Virus/Botnet activity or malicious actions

## Recommended Actions

Negotiate the source if it is your customer, or ignore

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
from_ip | ip_address | {{ yes }} | From IP
to_ip | ip_address | {{ no }} | To IP
from_side | str | {{ yes }} | From Side
proto | str | {{ yes }} | Protocol
open_flows | int | {{ yes }} | Open Flows
suspected_flows | int | {{ yes }} | Suspected Flows
action | str | {{ yes }} | Action

## Alarms

### Raising alarms

`Vendor | Cisco | SCOS | Security | Attack | Attack Detected` events may raise following alarms:

Alarm Class | Description
--- | ---
[Vendor \| Cisco \| SCOS \| Security \| Attack \| Attack Detected](../../../../../../alarm-classes/vendor/cisco/scos/security/attack/attack-detected.md) | Attack Detected
