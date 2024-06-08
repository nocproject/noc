# contacts Model Interface

Administrative, billing and technical contacts for container
(PoP, Room, Rack)

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `has_contacts` | bool | Object can hold contact information | {{ yes }} | {{ yes }} |
| `administrative` | str | Administrative contacts, including access and passes | {{ no }} | {{ no }} |
| `billing` | str | Billing contacts, including agreement negotiations, bills, and payments | {{ no }} | {{ no }} |
| `technical` | str | Technical contacts, including on-site engineering | {{ no }} | {{ no }} |

<!-- table end -->

## Examples

```json
{
  "contacts": {
    "has_contacts": "true"
  }
}
```
