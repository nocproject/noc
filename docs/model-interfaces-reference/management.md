# management Model Interface

[Managed Object](../concepts/managed-object/index.md) binding
Binding inventory object with Managed Object(MO) Service Activation(SA)
One MO can be associated with several inventory objects(virtual chassis, switches in the stack)

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `managed` | bool | Object can be bind to the ManagedObject | {{ no }} | {{ yes }} |
| `managed_object` | int | Managed Object id | {{ no }} | {{ no }} |

<!-- table end -->

## Examples

```json
{
  "management": {
    "managed": true,
    "managed_object": 888
  }
}
```
