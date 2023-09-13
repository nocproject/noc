---
uuid: 67353603-b8d2-4887-bf80-19496713747d
---
# Network | NTP | Lost synchronization

NTP synchronization with its peer has been lost

## Symptoms

## Probable Causes

NTP synchronization with its peer has been lost

## Recommended Actions

Perform the following actions:
   Check the network connection to the peer.
   Check to ensure that NTP is running on the peer.
   Check that the peer is synchronized to a stable time source.
   Check to see if the NTP packets from the peer have passed the validity tests specified in RFC1305.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
server_name | str | {{ no }} | NTP server name
server_address | ip_address | {{ no }} | NTP server IP address
