# rackmount Model Interface

Rack mounted equipment. Used to store position in rack.

`side` must be one of:

| Value | Description               |
| ----- | ------------------------- |
| `f`   | Mounted at the front side |
| `r`   | mounted at the rear side  |

In case of mismounting of the equipment it may be really shifted to one or two holes.
The `shift` parameter may be one of following:

| Value | Description                                  |
| ----- | -------------------------------------------- |
| 0     | fit to the unit                              |
| 1     | displacement 1 hole up relative to the unit  |
| 2     | displacement 2 holes up relative to the unit |

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `units` | float | Size in units | {{ yes }} | {{ yes }} |
| `position` | int | Bottom rack position (in units) | {{ no }} | {{ no }} |
| `side` | str | Mounting side (f/r) | {{ no }} | {{ no }} |
| `shift` | int | Shift 0/1/2 holes up | {{ no }} | {{ no }} |

<!-- table end -->

## Examples

```json
{
  "rackmount": {
     "units": 1.0
  }
}
```
