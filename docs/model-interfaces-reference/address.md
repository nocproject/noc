# address Model Interface

`address` model interface contains binding to external GIS system
and allows to store various address details

## Variables
<!-- table start -->
| Name          | Type | Description        | Required  | Constant  |
| ------------- | ---- | ------------------ | --------- | --------- |
| `has_address` | bool | Object has address | {{ yes }} | {{ yes }} |
| `id`          | str  | Address id         | {{ yes }} | {{ no }}  |
| `text`        | str  | Address as a text  | {{ yes }} | {{ no }}  |

<!-- table end -->

## Examples

``` json
{
    "address": {
        "has_addreess": true,
        "id": 203566,
        "address": "Milano, piazza del Duomo, 1"
    }
}
```