# IPPool

Metrics for DHCP and NAT pools Statistics

## Table Structure
The `IPPool` metric scope is stored
in the `ippool` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |
| service | sa.Service |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::ippool::name::*` |  | name |
| `noc::ippool::type::*` |  | type |
| `noc::ippool::prefix::*` |  | prefix |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="dhcp-pool-leases-active"></a>dhcp_pool_leases_active | UInt32 | DHCP \| Pool \| Leases \| Active | Number of active DHCP leases. | None | 1 | 1 |
| <a id="dhcp-pool-leases-active-percent"></a>dhcp_pool_leases_active_percent | UInt8 | DHCP \| Pool \| Leases \| Active \| Percent | Percent of active DHCP leases. | % | % | 1 |
| <a id="dhcp-pool-leases-free"></a>dhcp_pool_leases_free | UInt64 | DHCP \| Pool \| Leases \| Free | Number of free DHCP leases. | None | 1 | 1 |
| <a id="dhcp-pool-leases-total"></a>dhcp_pool_leases_total | UInt64 | DHCP \| Pool \| Leases \| Total | Number of total DHCP leases. | None | 1 | 1 |