# stack Model Interface

Indication of stack/virtual chassis/cluster

## Variables

| Name      | Type | Description           | Required | Conastant | Default |
| --------- | ---- | --------------------- | -------- | --------- | ------- |
| stackable | bool | Object can be stacked | {{ no }} | {{ yes }} |         |
| member    | str  | Stack member id       | {{ no }} | {{ no }}  |         |

## Examples

```json
{
  "stack": {
    "stackable": true
  }
}
```
