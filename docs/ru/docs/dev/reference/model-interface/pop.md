---
0f161fa9-5b69-4bbe-9efb-c6f80814305a
---

# pop Model Interface

Point of present

## Variables

| Name   | Type   | Description   | Required         | Constant         | Default   |
| ------ | ------ | ------------- | ---------------- | ---------------- | --------- |
| level  | int    | PoP level     | {{ yes }} | {{ yes }} |           |

Levels of PoP:

| Type          |   Level | Description                     |
| ------------- | ------- | ------------------------------- |
| International |      70 | International points of present |
| National      |      60 | National points of present      |
| Regional      |      50 | Regional points of present      |
| Core          |      40 | Metro Core                      |
| Agregation    |      30 | Agregation nodes                |
| Access        |      20 | Access nodes                    |
| Client        |      10 | Customer premises               |

## Examples

```json
{
  "pop": {
    "level": 50
  }
}
```
