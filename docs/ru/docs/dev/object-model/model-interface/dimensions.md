---
6aa71d8c-c4c7-4cca-91a5-3fc1af708f65
---

# dimensions Model Interface

A measurement of equipment in a particular direction, especially its height, length, or width:

## Variables

| Name    | Type   | Description               | Required         | Constant         | Default |
| ------- | ------ | ------------------------- | ---------------- | ---------------- | --------|
|width    | Int    | width in mm               | {{ yes }} | {{ yes }} |         |
|depth    | Int    | depth in mm               | {{ yes }} | {{ yes }} |         |
|height   | Int    | height in mm              | {{ yes }} | {{ yes }} |         |

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
