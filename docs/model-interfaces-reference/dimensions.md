# dimensions Model Interface

A measurement of equipment in a particular direction, especially its height, length, or width:

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `depth` | int | Object's depth in mm | {{ yes }} | {{ yes }} |
| `height` | int | Object's height in mm | {{ yes }} | {{ yes }} |
| `width` | int | Object's width in mm | {{ yes }} | {{ yes }} |

<!-- table end -->

## Examples

```json
{
  "dimensions": {
    "depth": 220,
    "height": 43.6,
    "width": 442
  }
}
```
