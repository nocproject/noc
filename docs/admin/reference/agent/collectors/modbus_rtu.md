# modbus_rtu collector

`modbus_rtu` collector performs Modbus RTU requests over the serial line
to collect performance data.

## Configuration

| Parameter       | Type             | Default       | Description                                                                                 |
| --------------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`            | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`          | String           |               | Must be `modbus_rtu`                                                                        |
| `service`       | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval`      | Integer          |               | Repetition interval in seconds                                                              |
| `labels`        | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |
| `serial_path`   | String           |               | Path to the serial port device (i.e. `/dev/ttyS1`)                                          |
| `slave`         | Integer          |               | Modbus RTU slave id                                                                         |
| `baud_rate`     | Integer          |               | Serial port speed                                                                           |
| `data_bits`     | Integer          |               | Serial port data bits: 5, 6, 7 or 8                                                         |
| `parity`        | String           | `none`        | Serial port parity, either `none`, `even` or `odd`                                          |
| `stop_bits`     | Integer          |               | Serial port stop bits, either `1` or `2`                                                    |
| `register`      | Integer          |               | Starting register of modbus request, zero-based                                             |
| `register_type` | String           | `holding`     | Modbus request type. Either `holding`, `input` or `coil`                                    |
| `format`        | String           |               | Expected response format. See [Response format](#response-format) for details               |
| `timeout_ms`    | Integer          | 5000          | Request timeout, ms.                                                                        |

!!! warning "Check address notation"

    Take note the starting register address is zero-based, while vendors
    can document the registers starting from 1. Refer to the vendor documentation
    and subtract 1 when necessary.

## Response Format

Modbus' response is as an array of 16-bit integers. Actual data encoding
should be set as `format` parameter. Some encodings may require reading
2 or 4 adjacent registers.

| Format   | Count | Description                                  |
| -------- | ----- | -------------------------------------------- |
| `i16_be` | 1     | 16-bit signed integer, big-endian.           |
| `u16_be` | 1     | 16-bit unsigned integer, big-endian.         |
| `i32_be` | 2     | 32-bit signed integer, big-endian            |
| `i32_le` | 2     | 32-bit signed integer, low-endian            |
| `i32_bs` | 2     | 32-bit signed integer, big-endian, swapped   |
| `i32_ls` | 2     | 32-bit signed integer, low-endian, swapped   |
| `u32_be` | 2     | 32-bit unsigned integer, big-endian          |
| `u32_le` | 2     | 32-bit unsigned integer, low-endian          |
| `u32_bs` | 2     | 32-bit unsigned integer, big-endian, swapped |
| `u32_ls` | 2     | 32-bit unsigned integer, low-endian, swapped |
| `f32_be` | 2     | 32-bit floating point, big-endian            |
| `f32_le` | 2     | 32-bit floating point, low-endian            |
| `f32_bs` | 2     | 32-bit floating point, big-endian, swapped   |
| `f32_ls` | 2     | 32-bit floating point, low-endian, swapped   |

### Big/Low/Swapped endian

32-bit integer `0x01020304` stored as a sequence of 4 octets. 4 different
approaches widely used between modbus devices:

| Format                   |   1 |   2 |   3 |   4 |
| ------------------------ | --: | --: | --: | --: |
| Big-endian (be)          |  01 |  02 |  03 |  04 |
| Low-endian (le)          |  04 |  03 |  02 |  01 |
| Big-endian, swapped (bs) |  02 |  01 |  04 |  03 |
| Low-endian, swapped (ls) |  03 |  04 |  01 |  02 |

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
