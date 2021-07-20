# modbus_rtu collector

`modbus_rtu` collector performs Modbus RTU requests over the serial line
to collect performance data.

## Configuration

| Parameter       | Type             | Default       | Description                                                                                 |
| --------------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`            | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`          | String           |               | Must be `dns`                                                                               |
| `service`       | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval`      | Integer          |               | Repetition interval in seconds                                                              |
| `labels`        | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |
| `serial_path`   | String           |               | Path to the serial port device (i.e. `/dev/ttyS1`)                                          |
| `slave`         | Integer          |               | Modbus RTU slave id                                                                         |
| `baud_rate`     | Integer          |               | Serial port speed                                                                           |
| `data_bits`     | Integer          |               | Serial port data bits: 5, 6, 7 or 8                                                         |
| `parity`        | String           | `none`        | Serial port parity, either `none`, `even` or `odd`                                          |
| `stop_bits`     | Integer          |               | Serial port stop bits, either `1` or `2`                                                    |
| `register`      | Integer          |               | Starting register of modbus request                                                         |
| `count`         | Integer          | `1`           | Amount of 16-bit registers to read                                                          |
| `register_type` | String           | `holding`     | Modbus request type. Either `holding`, `input` or `coil`                                    |
| `format`        | String           |               | Expected response format. See [Response format](#response-format) for details               |

## Response Format

Modbus' response is as an array of 16-bit integers. Actual data encoding
may be set as `format` parameter. Some encodings may require reading of
2 or 4 registers (`count` must be set to 2 or 4).

| Format   | Count | Description                          |
| -------- | ----- | ------------------------------------ |
| `i16_be` | 1     | 16-bit signed integer, big-endian.   |
| `u16_be` | 1     | 16-bit unsigned integer, big-endian. |

## Collected Metrics

| Metric      | Metric Type | Platform | Description        |
| ----------- | ----------- | -------- | ------------------ |
| `ts`        |             | All      | ISO 8601 Timestamp |
| `collector` |             | All      | Collector Id       |
| `labels`    |             | All      | List of labels     |
|             |             |          |                    |
| `value`     |             | All      | Measured value     |

## Compilation Features

Enable `modbus_rtu` feature during compiling the agent (Enabled by default).
