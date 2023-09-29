# Sensor

Sensor-related metrics

## Table Structure
The `Sensor` metric scope is stored
in the `sensor` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| sensor | inv.Sensor |
| managed_object | sa.ManagedObject |
| object | inv.Object |
| service | sa.Service |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::chassis::*` | chassis |  |
| `noc::slot::*` | slot |  |
| `noc::module::*` | module |  |
| `noc::sensor::*` |  | name |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="sensor-status"></a>status | UInt8 | Sensor \| Status | Sensor status value |  | status | 1 |
| <a id="sensor-value"></a>value | Float32 | Sensor \| Value | Numeric value of the sensor | c | 1 | 1 |
| <a id="sensor-value-delta"></a>value_delta | Float32 | Sensor \| Value Delta | For counters, the difference between the current and previous values | c | 1 | 1 |
| <a id="sensor-value-raw"></a>value_raw | Float32 | Sensor \| Value Raw | Numeric value of the sensor before normalization | c | 1 | 1 |