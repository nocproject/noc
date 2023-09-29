# Environment

Environment-related metrics

## Table Structure
The `Environment` metric scope is stored
in the `environment` ClickHouse table.

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
| `noc::sensor::*` |  | sensor |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="environment-battery-capacity-level"></a>battery_capacity_level | UInt8 | Environment \| Battery \| Capacity \| Level | Metric Battery Level (%) | % | % | 1 |
| <a id="environment-electric-current"></a>elec_current | Float32 | Environment \| Electric Current | The metric for the Electric Сurrent | mA | A | m |
| <a id="environment-energy-consumption"></a>energy_consumption | Float32 | Environment \| Energy Consumption | The metric for the Energy consumption (kWh) | kWh | W*h | k |
| <a id="environment-power"></a>power_consume | UInt16 | Environment \| Power | Metric for device Consume Power (W) | W | W | 1 |
| <a id="environment-power-input-status"></a>power_input_status | Int8 | Environment \| Power \| Input \| Status | Power input status |  | status | 1 |
| <a id="environment-pulse"></a>pulse | UInt32 | Environment \| Pulse | Metric for pulse output. The number of impulses since switching on. |  | 1 | 1 |
| <a id="environment-sensor-status"></a>sensor_status | Int8 | Environment \| Sensor Status | Metric for displaying the status of sensors |  | status | 1 |
| <a id="environment-temperature"></a>temperature | Int16 | Environment \| Temperature | Temparature, in Celsium | C | C | 1 |
| <a id="environment-voltage"></a>voltage | Float32 | Environment \| Voltage | The metric for the Voltage (V) | V | VDC | 1 |