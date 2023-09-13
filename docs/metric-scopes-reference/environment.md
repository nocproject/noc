---
uuid: 832bb31b-1441-477f-ac69-0b21d2761f06
---
# Environment Metric Scope

Environment-related metrics

## Data Table

ClickHouse Table: `environment`

| Field                                                                                     | Type                          | Description                                                                                                    |
| ----------------------------------------------------------------------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------- |
| date                                                                                      | Date                          | Measurement Date                                                                                               |
| ts                                                                                        | DateTime                      | Measurement Timestamp                                                                                          |
| path                                                                                      | Array of String {{ complex }} | Measurement Path                                                                                               |
| {{ tab }} `chassis`                                                                       | {{ no }}                      |
| {{ tab }} `slot`                                                                          | {{ no }}                      |
| {{ tab }} `module`                                                                        | {{ no }}                      |
| {{ tab }} `name`                                                                          | {{ no }}                      |
| [battery_capacity_level](../metric-types-reference/environment/battery/capacity/level.md) | UInt8                         | [Environment \| Battery \| Capacity \| Level](../metric-types-reference/environment/battery/capacity/level.md) |
| [elec_current](../metric-types-reference/environment/electric-current.md)                 | Float32                       | [Environment \| Electric Current](../metric-types-reference/environment/electric-current.md)                   |
| [energy_consumption](../metric-types-reference/environment/energy-consumption.md)         | Float32                       | [Environment \| Energy Consumption](../metric-types-reference/environment/energy-consumption.md)               |
| [power_consume](../metric-types-reference/environment/power.md)                           | UInt16                        | [Environment \| Power](../metric-types-reference/environment/power.md)                                         |
| [power_input_status](../metric-types-reference/environment/power/input/status.md)         | Int8                          | [Environment \| Power \| Input \| Status](../metric-types-reference/environment/power/input/status.md)         |
| [pulse](../metric-types-reference/environment/pulse.md)                                   | UInt32                        | [Environment \| Pulse](../metric-types-reference/environment/pulse.md)                                         |
| [sensor_status](../metric-types-reference/environment/sensor-status.md)                   | Int8                          | [Environment \| Sensor Status](../metric-types-reference/environment/sensor-status.md)                         |
| [temperature](../metric-types-reference/environment/temperature.md)                       | Int16                         | [Environment \| Temperature](../metric-types-reference/environment/temperature.md)                             |
| [voltage](../metric-types-reference/environment/voltage.md)                               | Float32                       | [Environment \| Voltage](../metric-types-reference/environment/voltage.md)                                     |
