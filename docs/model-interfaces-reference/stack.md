# stack Model Interface

Indication of stack/virtual chassis/cluster. If chassis belongs to the
stack, the `stack` model interface will be initialized by [asset](../discovery-reference/box/asset.md)
discovery.

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `stackable` | bool | Object can be stacked | {{ no }} | {{ yes }} |
| `member` | str | Stack member id | {{ no }} | {{ no }} |

<!-- table end -->

## Examples

```json
{
  "stack": {
    "stackable": true
  }
}
```
