# dwdm Model Interface

`dwdm` model interface holds DWDM transponders capabilities.

## Variables
<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `min_rx_tx_frequency` | float | Minimum supported Tx/Rx Frequency, THz | {{ yes }} | {{ yes }} |
| `max_rx_tx_frequency` | float | Maximum supported Tx/Rx Frequency, THz | {{ yes }} | {{ yes }} |
| `min_frequency_step` | float | Minimum frequency change step, GHz | {{ yes }} | {{ yes }} |
| `tx_power` | float | Transmit level, dBm | {{ no }} | {{ no }} |
| `tx_frequency` | float | Transmit frequency, THz | {{ no }} | {{ no }} |
| `rx_frequency` | float | Receive frequency, THz | {{ no }} | {{ no }} |

<!-- table end -->

