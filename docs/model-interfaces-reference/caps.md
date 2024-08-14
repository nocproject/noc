# caps Model Interface

`caps` model interface holds additional object's capabilities.

## Variables
<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `dynamic_crossing` | bool | Object supports dynamic crossing | {{ no }} | {{ no }} |
| `multi_slot` | int | An oversized card which occupies multiple slots | {{ no }} | {{ no }} |

<!-- table end -->

## Examples

``` json
{
    "caps": {
        "multi_slot": 2,
        "dynamic_crossing": true
    }
}
```