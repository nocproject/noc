# rack Model Interface

Rack enclosures.

Doors configuration must be one of the following letters:

| Value | Description                          |
| ----- | ------------------------------------ |
| `o`   | open, hasn't door                    |
| `c`   | closed, blank door                   |
| `l`   | one section, opens on the left side  |
| `r`   | one section, opens on the right side |
| `2`   | two sections                         |


## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `units` | int | Internal height in units | {{ yes }} | {{ yes }} |
| `width` | int | Max. equipment width in mm | {{ yes }} | {{ yes }} |
| `depth` | int | Max. equipment depth in mm | {{ yes }} | {{ yes }} |
| `front_door` | str | Front door configuration | {{ yes }} | {{ yes }} |
| `rear_door` | str | Rear door configuration | {{ yes }} | {{ yes }} |

<!-- table end -->


## Examples

```json
{
  "rack": {
    "depth": 600,
    "front_door": "l",
    "rear_door": "c",
    "units": 4,
    "width": 600
  }
}
```
