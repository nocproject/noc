---
e8e9a35f-d051-4b11-8e0b-0d14dcbdffb1
---

# asset Model Interface

Inventory references, asset and serial numbers

## Variables

| Name            | Type        | Description                               | Required         | Constant         | Default |
| --------------- | ----------- | ----------------------------------------- | ---------------- | ---------------- |---------|
| part_no         | String List | Internal vendor's part number             | {{ yes }} | {{ yes }} |         |
|                 |             | as shown by diagnostic commands           |                  |                  |         |
| order_part_no   | String List | Vendor's [FRU](../../../glossary.md#fru) as shown | {{ no }} | {{ yes }} |         |
|                 |             | in catalogues and price lists             |                  |                  |         |
| serial          | String      | Item's serial number                      | {{ no }} |                  |         |
| revision        | String      | Item's hardware revision                  | {{ no }} |                  |         |
| asset_no        | String      | Item's asset number, used for             | {{ no }} |                  |         |
|                 |             | asset tracking in accounting              |                  |                  |         |
|                 |             | system                                    |                  |                  |         |
| mfg_date        | String      | Manufacturing date in                     | {{ no }} |                  |         |
|                 |             | YYYY-MM-DD format                         |                  |                  |         |
| cpe_22          | String      | CPE v2.2 identification string            | {{ no }} | {{ yes }} |         |
| cpe_23          | String      | CPE v2.3 identification string            | {{ no }} | {{ yes }} |         |
| min_serial_size | Integer     | Minimal valid serial number size          | {{ no }} | {{ yes }} |         |
| max_serial_size | Integer     | Maximal valid serial number size          | {{ no }} | {{ yes }} |         |
| serial_mask     | String      | Regular expression to check serial number | {{ no }} | {{ yes }} |         |

## Examples

```json
{
  "asset": {
    "order_part_no": ["MX-MPC2E-3D-Q"],
    "part_no": ["750-038493"]
  }
}
```
