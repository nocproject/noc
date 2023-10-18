# twinax Model Interface

Twinax transceiver (two transceivers connected by cable in the assembly).
Both transceivers have the same serial number and can be inserted in one or two managed object.

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `twinax` | bool | Object is the twinax transceiver | {{ yes }} | {{ yes }} |
| `alias` | str | Virtual connection name for ConnectionRule | {{ yes }} | {{ yes }} |
| `connection1` | str | Connection name for first side of twinax | {{ yes }} | {{ yes }} |
| `connection2` | str | Connection name for second side of twinax | {{ yes }} | {{ yes }} |

<!-- table end -->