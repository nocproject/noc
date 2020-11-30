---
uuid: 53b4f0da-3915-4573-adc3-3084a22e5516
---
# Vendor | Cisco | SCOS | Security | Attack | Attack Detected

## Symptoms

Possible DoS/DDoS traffic from source

## Probable Causes

Virus/Botnet activity or malicious actions

## Recommended Actions

Negotiate the source if it is your customer, or ignore

## Variables

Variable | Description | Default
--- | --- | ---
from_ip | From IP | {{ no }}
to_ip | To IP | {{ no }}
from_side | From Side | {{ no }}
proto | Protocol | {{ no }}
open_flows | Open Flows | {{ no }}
suspected_flows | Suspected Flows | {{ no }}
action | Action | {{ no }}

## Events

### Opening Events
`Vendor | Cisco | SCOS | Security | Attack | Attack Detected` may be raised by events

Event Class | Description
--- | ---
[Vendor \| Cisco \| SCOS \| Security \| Attack \| Attack Detected](../../../../../../event-classes/vendor/cisco/scos/security/attack/attack-detected.md) | Attack Detected

### Closing Events
`Vendor | Cisco | SCOS | Security | Attack | Attack Detected` may be cleared by events

Event Class | Description
--- | ---
[Vendor \| Cisco \| SCOS \| Security \| Attack \| End-of-attack detected](../../../../../../event-classes/vendor/cisco/scos/security/attack/end-of-attack-detected.md) | Clear Attack Detected
