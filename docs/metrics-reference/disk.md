# Disk

Disk metrics

## Table Structure
The `Disk` metric scope is stored
in the `disk` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::device::*` |  | device |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="disk-usage"></a>disk_usage_b | UInt64 | Disk \| Usage | Disk Usage byte | bytes | byte | 1 |
| <a id="disk-usage-percent"></a>disk_usage_p | UInt8 | Disk \| Usage Percent | Disk Usage % | % | % | 1 |