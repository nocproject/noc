---
2bfdfe3a-78dc-429c-99c7-a3db73d3e491
---

# management Model Interface

ManagedObject binding
Binding inventory object with Managed Object(MO) Service Activation(SA)
One MO can be associated with several inventory objects(virtual chassis, switches in the stack)

## Variables

| Name           | Type   | Description                             | Required         | Constant         | Default   |
| -------------- | ------ | --------------------------------------- | ---------------- | ---------------- | --------- |
| managed        | bool   | Object can be bind to the ManagedObject | {{ no }} | {{ yes }} |           |
| managed_object | int    | Managed Object id                       | {{ no }} | {{ no }} |           |

## Examples

```json
{
  "management": {
    "managed": true
  }
}
```
