# airflow Model Interface

Airflow direction for cooling. May be set for rack to show desired
airflow movement from _cold_ to _hot_ area, and for equipment to show
constructive air movement.

The directions are specified by single letter and must be one
of following values:

| Value | Description |
| ----- | ----------- |
| `f`   | forward     |
| `r`   | rear        |
| `b`   | bottom      |
| `t`   | top         |
| `l`   | left        |
| `r`   | right       |


## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `exhaust` | str | Hot exhaust direction | {{ yes }} | {{ yes }} |
| `intake` | str | Cold intake direction | {{ yes }} | {{ yes }} |

<!-- table end -->


## Examples

```json
{
  "airflow": {
    "exhaust": "l",
    "intake": "r"
  }
}
```
