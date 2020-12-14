---
uuid: 832bb31b-1441-477f-ac69-0b21d2761f06
---
# Environment Metric Scope

Environment-related metrics

## Data Table

ClickHouse Table: `environment`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `chassis` | {{ no }} | 
{{ tab }} `slot` | {{ no }} | 
{{ tab }} `module` | {{ no }} | 
{{ tab }} `name` | {{ no }} | 
[battery_capacity_level](../types/environment/battery/capacity/level.md) | UInt8 | [Environment \| Battery \| Capacity \| Level](../types/environment/battery/capacity/level.md)
[elec_current](../types/environment/electric-current.md) | Float32 | [Environment \| Electric Current](../types/environment/electric-current.md)
[energy_consumption](../types/environment/energy-consumption.md) | Float32 | [Environment \| Energy Consumption](../types/environment/energy-consumption.md)
[power_consume](../types/environment/power.md) | UInt16 | [Environment \| Power](../types/environment/power.md)
[power_input_status](../types/environment/power/input/status.md) | Int8 | [Environment \| Power \| Input \| Status](../types/environment/power/input/status.md)
[pulse](../types/environment/pulse.md) | UInt32 | [Environment \| Pulse](../types/environment/pulse.md)
[sensor_status](../types/environment/sensor-status.md) | Int8 | [Environment \| Sensor Status](../types/environment/sensor-status.md)
[temperature](../types/environment/temperature.md) | Int16 | [Environment \| Temperature](../types/environment/temperature.md)
[voltage](../types/environment/voltage.md) | Float32 | [Environment \| Voltage](../types/environment/voltage.md)
