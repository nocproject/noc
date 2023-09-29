# Multicast

Scope for Multicast protocols metrics

## Table Structure
The `Multicast` metric scope is stored
in the `multicast` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::multicast::group::*` | group |  |
| `noc::multicast::channel::*` | channel |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="multicast-channel-bandwidth-percent"></a>c_bandwidth_percent | UInt8 | Multicast \| Channel \| Bandwidth \| Percent | Used Bandwidth in Percent | % | % | 1 |
| <a id="multicast-channel-bandwidth-used"></a>c_bandwidth_used | Float32 | Multicast \| Channel \| Bandwidth \| Used | Used Bandwidth (bps) | bps | bit/s | 1 |
| <a id="multicast-channel-group-count"></a>c_group_count | UInt8 | Multicast \| Channel \| Group \| Count | Used multicast groups on channel |  | 1 | 1 |
| <a id="multicast-group-bitrate-in"></a>g_bitrate_in | UInt64 | Multicast \| Group \| Bitrate \| In | Input Bitrate (bps) | bps | bit/s | 1 |
| <a id="multicast-group-bitrate-out"></a>g_bitrate_out | UInt64 | Multicast \| Group \| Bitrate \| Out | Output Bitrate (bps) | bps | bit/s | 1 |
| <a id="multicast-group-status"></a>g_status | Int8 | Multicast \| Group \| Status | Multicast Group status 1 - Ok, 0 - Off, -1 - Error  |  | status | 1 |