# modbus model interface

[Modbus](https://en.wikipedia.org/wiki/Modbus) endpoint configuration.

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `type` | str | Modbus type: RTU, ASCII or TCP | {{ yes }} | {{ yes }} |
| `slave_id` | int | Modbus slave id | {{ yes }} | {{ no }} |
| `speed` | int | Bus speed, baud/s | {{ no }} | {{ no }} |
| `bits` | int | Bus baud size | {{ no }} | {{ no }} |
| `parity` | bool | Bus parity | {{ no }} | {{ no }} |
| `stop` | int | Bus stop bits | {{ no }} | {{ no }} |

<!-- table end -->

## Examples

```json
{
  "type": "RTU",
  "slave_id": 3,
  "speed": 115200,
  "bits": 8,
  "parity": false,
  "stop": 1
}
```
