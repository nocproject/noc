# FileSystem

FileSystem

## Table Structure
The `FileSystem` metric scope is stored
in the `filesystem` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| agent | pm.Agent |
| object | inv.Object |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::device::*` |  | device |
| `noc::fs::mountpoint::*` |  | mountpoint |
| `noc::fs::type::*` |  |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |