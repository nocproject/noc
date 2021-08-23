# modbus_tcp collector

`modbus_tcp` collector performs Modbus TCP requests to collect performance data.

## Configuration

| Parameter       | Type             | Default       | Description                                                                                 |
| --------------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`            | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`          | String           |               | Must be `modbus_tcp`                                                                        |
| `service`       | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval`      | Integer          |               | Repetition interval in seconds                                                              |
| `labels`        | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |
| `address`       | String           |               | IP address of Modbus TCP server                                                             |
| `port`          | Integer          |               | Port of Modbus TCP server                                                                   |
| `register`      | Integer          |               | Starting register of modbus request, zero-based                                             |
| `register_type` | String           | `holding`     | Modbus request type. Either `holding`, `input` or `coil`                                    |
| `format`        | String           |               | Expected response format. See [Response format](modbus_rtu.md#response-format) for details  |
| `timeout_ms`    | Integer          | 5000          | Request timeout, ms.                                                                        |
| `slave`         | Integer          | 255           | Optional slave id, see note below.                                                          |

!!! warning "Check address notation"

    Take note the starting register address is zero-based, while vendors
    can document the registers starting from 1. Refer to the vendor documentation
    and subtract 1 when necessary.

!!! note "On Slave ID"

    Modbus TCP specification insists on using slave id of 255 for TCP connections.
    Meanwhile shome implmenetations await broadcast id (0). Modbust TCP-to-RTU
    proxies also may expect explicit slave id to process the request.

## Collected Metrics

| Metric      | Metric Type | Platform | Description        |
| ----------- | ----------- | -------- | ------------------ |
| `ts`        |             | All      | ISO 8601 Timestamp |
| `collector` |             | All      | Collector Id       |
| `labels`    |             | All      | List of labels     |
|             |             |          |                    |
| `value`     |             | All      | Measured value     |

## Compilation Features

Enable `modbus_tcp` feature during compiling the agent (Enabled by default).
