# modbus_tcp collector

`modbus_tcp` collector performs Modbus TCP requests to collect performance data.

## Configuration

| Parameter       | Type             | Default       | Description                                                                                 |
| --------------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`            | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`          | String           |               | Must be `dns`                                                                               |
| `service`       | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval`      | Integer          |               | Repetition interval in seconds                                                              |
| `labels`        | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |
| `address`       | String           |               | IP address of Modbus TCP server                                                             |
| `port`          | Integer          |               | Port of Modbus TCP server                                                                   |
| `register`      | Integer          |               | Starting register of modbus request                                                         |
| `count`         | Integer          | `1`           | Amount of 16-bit registers to read                                                          |
| `register_type` | String           | `holding`     | Modbus request type. Either `holding`, `input` or `coil`                                    |
| `format`        | String           |               | Expected response format. See [Response format](modbus_rtu.md#response-format) for details  |

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
