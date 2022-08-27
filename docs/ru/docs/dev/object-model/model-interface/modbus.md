---
uuid: 4067ca6c-d8a7-43af-b22a-6232fde21576
---

# modbus model interface

[Modbus](https://en.wikipedia.org/wiki/Modbus) endpoint configuration.

## Variables

| Name       | Type | Description               | Required  | Constant |  Default |
| ---------- | ---- | ------------------------- | --------- | -------- | -------: |
| `type`     | str  | Modbus Type               | {{ yes }} | {{ no }} | {{ no }} |
| `slave_id` | int  | Modbus Slave Id           | {{ yes }} | {{ no }} | {{ no }} |
| `speed`    | int  | Serial bus speed (baud/s) | {{ no }}  | {{ no }} |     9600 |
| `bits`     | int  | Serial bus baud size      | {{ no }}  | {{ no }} |        8 |
| `parity`   | bool | Serial bus parity bit     | {{ no }}  | {{ no }} |    False |
| `stop`     | int  | Serial bus stop bits      | {{ no }}  | {{ no }} |        1 |

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
