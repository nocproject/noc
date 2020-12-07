---
uuid: 0ced5d24-225f-422b-8c9c-8d8ae5c480a5
---
# Network | OAM | Discovery Timeout

Client discovery timeout

## Symptoms

## Probable Causes

The Ethernet OAM client on the specified interface has not received any OAMPDUs in the number of seconds for timeout that were configured by the user. The client has exited the OAM session.

## Recommended Actions

No action is required.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
