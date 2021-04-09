---
uuid: a14aadb9-e0c9-4d8c-adf6-569f721322f8
---
# Network | DOCSIS | Unregistered Modem Deleted

CMTS deleted unregistered Cable Modem

## Symptoms

## Probable Causes

An unregistered cable modem has been deleted to avoid unaccounted bandwidth usage.

## Recommended Actions

Check the cable modem interface configuration for registration bypass, or check for errors in the TFTP configuration file. 

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ yes }} | Cable Modem MAC
