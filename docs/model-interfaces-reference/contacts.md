# contacts Model Interface

Administrative, billing and technical contacts for container
(PoP, Room, Rack)

## Variables

| Name           | Type    | Description                   | Required  | Constant  | Default |
| -------------- | ------- | ----------------------------- | --------- | --------- | ------- |
| has_contacts   | Boolean | Object can hold               | {{ yes }} | {{ yes }} | true    |
|                |         | contact information           |           |           |         |
| administrative | String  | Administrative contacts       | {{ no }}  | {{ no }}  |         |
|                |         | including access and passes   |           |           |         |
| billing        | String  | Billing contacts, including   | {{ no }}  | {{ no }}  |         |
|                |         | agreement negotiations,       |           |           |         |
|                |         | bills and payments            |           |           |         |
| technical      | String  | Technical contacts,           | {{ no }}  | {{ no }}  |         |
|                |         | including on-site engineering |           |           |         |

## Examples

```json
{
  "contacts": {
    "has_contacts": "true"
  }
}
```
