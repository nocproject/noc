---
a3c13162-a7bf-420c-99e3-5977a5f0f47e
---

# power Model Interface

Object's power consumption

## Variables

| Name         | Type   | Description                                   | Required         | Constant         | Default   |
| ------------ | ------ | --------------------------------------------- | ---------------- | ---------------- | --------- |
| power        | float  | Object's own power consumption in `W`         | {{ yes }} | {{ yes }} |           |
| is_recursive | bool   | Add nested object's power consumption if true | {{ yes }} | {{ yes }} | false     |

Power consumption may be exact (is_recursive = false), when power represents total power consumption,
or recursive (is_recursive = true), when total power is a sum of power and a power consumption of all nested elements

## Examples

```json
{
  "power": {
    "power": 50.0
  }
}
```