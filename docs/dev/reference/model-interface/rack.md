---
a15da7b7-98de-4843-b256-0da049137833
---

# rack Model Interface

Rack enclosures

## Variables

| Name       | Type   | Description                               | Required         | Constant         | Default   |
| ---------- | ------ | ----------------------------------------- | ---------------- | ---------------- | --------- |
| units      | int    | Internal height in units                  | {{ yes }} | {{ yes }} |           |
| width      | int    | Max. equipment width in mm                | {{ yes }} | {{ yes }} |           |
| depth      | int    | Max. equipment depth in mm                | {{ yes }} | {{ yes }} |           |
| front_door | str    | Front door configuration                  | {{ yes }} | {{ yes }} |           |
|            |        |                                           |                  |                  |           |
|            |        |  `o` - open, hasn't door                    |                |                  |           |
|            |        |  `c` - closed, blank door                   |                |                  |           |
|            |        |  `l` - one section, opens on the left side  |                |                  |           |
|            |        |  `r` - one section, opens on the right side |                |                  |           |
|            |        |  `2` - two sections                         |                |                  |           |
| rear_door  | str    | Rear door configuration                   | {{ yes }} | {{ yes }} |           |
|            |        |                                           |                  |                  |           |
|            |        |  `o` - open, hasn't door                    |                |                  |           |
|            |        |  `c` - closed, blank door                   |                |                  |           |
|            |        |  `l` - one section, opens on the left side  |                |                  |           |
|            |        |  `r` - one section, opens on the right side |                |                  |           |
|            |        |  `2` - two sections                         |                |                  |           |


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
