# power Model Interface

Object's power consumption

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `is_recursive` | bool | Add nested object's power consumption if true | {{ yes }} | {{ yes }} |
| `power` | float | Object's own power consumption in W | {{ yes }} | {{ yes }} |

<!-- table end -->

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