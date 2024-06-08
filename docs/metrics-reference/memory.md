# Memory

Memory-related metrics

## Table Structure
The `Memory` metric scope is stored
in the `memory` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::chassis::*` | chassis |  |
| `noc::slot::*` | slot |  |
| `noc::module::*` | module |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="memory-heap"></a>heap | UInt8 | Memory \| Heap | Memory Heap in percents | % | % | 1 |
| <a id="memory-load-1min"></a>load_1min | UInt8 | Memory \| Load \| 1min | None | % | % | 1 |
| <a id="memory-total"></a>total | UInt64 | Memory \| Total | Memory total in bytes | bytes | byte | 1 |
| <a id="memory-usage"></a>usage | UInt8 | Memory \| Usage | Memory Usage in percents | % | % | 1 |
| <a id="memory-usage-5sec"></a>usage_5s | UInt8 | Memory \| Usage \| 5sec | Memory Usage in percents | % | % | 1 |
| <a id="memory-usage-bytes"></a>usage_bytes | UInt64 | Memory \| Usage \| Bytes | Memory usage in bytes | None | byte | 1 |