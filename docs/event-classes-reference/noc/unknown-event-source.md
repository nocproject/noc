---
uuid: 764bd643-9c5a-41bc-bf9b-89a1e44abe70
---
# NOC | Unknown Event Source

Unknown Event Source

## Symptoms

Events from particular device are ignored by Fault Management

## Probable Causes

Event's source address does not belong to any Managed Object's trap_source

## Recommended Actions

Add appropriative Managed Object or fix trap_source

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
ip | ip_address | {{ yes }} | Event SRC IP
collector_ip | ip_address | {{ yes }} | Collector's IP address
collector_port | int | {{ yes }} | Collector's port
activator | str | {{ yes }} | Activator pool
