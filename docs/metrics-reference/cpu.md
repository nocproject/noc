# CPU

CPU-related metrics

## Table Structure
The `CPU` metric scope is stored
in the `cpu` ClickHouse table.

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
| `noc::cpu::*` |  | name |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="cpu-load-1min"></a>load_1min | Float32 | CPU \| Load \| 1min | None | % | 1 | 1 |
| <a id="cpu-load-5min"></a>load_5min | Float32 | CPU \| Load \| 5min | None | % | 1 | 1 |
| <a id="cpu-usage-5sec"></a>load_5s | UInt8 | CPU \| Usage \| 5sec | CPU Usage in percents | % | % | 1 |
| <a id="cpu-usage"></a>usage | UInt8 | CPU \| Usage | CPU Usage in percents | % | % | 1 |