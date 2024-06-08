# VPN

Metrics for L2/L3 vpn tunnels.
Instance - VPN ID: use it for L2 VPN name
local_endpoint and remote_endpoint: For IPSEC it contains local IP and remote IP, for other type some string


## Table Structure
The `VPN` metric scope is stored
in the `vpns` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::instance::*` | instance |  |
| `noc::local_endpoint::*` | local_endpoint |  |
| `noc::remote_endpoint::*` | remote_endpoint |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |