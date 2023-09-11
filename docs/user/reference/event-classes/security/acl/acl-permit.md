---
uuid: 025058a2-881d-4a53-b572-f07dd37c0772
---
# Security | ACL | ACL Permit

Packet permitted by ACL

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
name | str | {{ no }} | ACL Name
proto | str | {{ no }} | Protocol
src_interface | interface_name | {{ no }} | Source Interface
src_ip | ip_address | {{ no }} | Source IP
src_port | int | {{ no }} | Source port
src_mac | mac | {{ no }} | Source MAC
dst_interface | interface_name | {{ no }} | Destination Interface
dst_ip | ip_address | {{ no }} | Destination IP
dst_port | int | {{ no }} | Destination port
count | int | {{ no }} | Packets count
flags | str | {{ no }} | Flags
