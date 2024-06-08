# pop Model Interface

Point of present

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `level` | int | PoP level | {{ yes }} | {{ yes }} |

<!-- table end -->

Levels of PoP:

| Type          | Level | Description                     |
| ------------- | ----- | ------------------------------- |
| International | 70    | International points of present |
| National      | 60    | National points of present      |
| Regional      | 50    | Regional points of present      |
| Core          | 40    | Metro Core                      |
| Agregation    | 30    | Agregation nodes                |
| Access        | 20    | Access nodes                    |
| Client        | 10    | Customer premises               |

## Examples

```json
{
  "pop": {
    "level": 50
  }
}
```
