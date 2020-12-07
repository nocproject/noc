---
uuid: ea244bae-6d36-40ec-bc24-e69a2c03a23b
---
# Network | IMPB | Dynamic IMPB entry is conflicting with static

Dynamic IMPB entry is conflicting with static

## Symptoms

Discard user connection attemps

## Probable Causes

## Recommended Actions

Check user IP and MAC, check DHCP database

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
ip | ip_address | {{ yes }} | User IP
mac | mac | {{ yes }} | User MAC
interface | interface_name | {{ yes }} | Affected interface
