---
uuid: 5228f878-37ba-46ea-bebf-97bcf5bbd16a
---
# Security | Attack | IP Spoofing

IP Spoofing detected

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
src_ip | ip_address | {{ yes }} | Source IP
src_mac | mac | {{ no }} | Source MAC

## Alarms

### Raising alarms

`Security | Attack | IP Spoofing` events may raise following alarms:

Alarm Class | Description
--- | ---
[Security \| Attack \| IP Spoofing](../../../alarm-classes/security/attack/ip-spoofing.md) | dispose
