# asset Model Interface

Inventory references, asset and serial numbers

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `part_no` | strlist | Internal vendor's part numbers, as shown by diagnostic commands | {{ yes }} | {{ yes }} |
| `order_part_no` | strlist | Vendor's FRU, as shown in catalogues and price lists | {{ no }} | {{ yes }} |
| `serial` | str | Item's serial number | {{ no }} | {{ no }} |
| `asset_no` | str | Item's asset number, used for an asset tracking in accounting system | {{ no }} | {{ no }} |
| `revision` | str | Item's hardware revision | {{ no }} | {{ no }} |
| `mfg_date` | str | Manufacturing date in YYYY-MM-DD format | {{ no }} | {{ no }} |
| `cpe_22` | str | CPE v2.2 identification string | {{ no }} | {{ yes }} |
| `cpe_23` | str | CPE v2.3 identification string | {{ no }} | {{ yes }} |
| `serial_mask` | str | Regular expression to check serial number | {{ no }} | {{ yes }} |
| `min_serial_size` | int | Minimal valid serial number size | {{ no }} | {{ yes }} |
| `max_serial_size` | int | Maximal valid serial number size | {{ no }} | {{ yes }} |

<!-- table end -->

## Examples

```json
{
  "asset": {
    "order_part_no": ["MX-MPC2E-3D-Q"],
    "part_no": ["750-038493"]
  }
}
```
