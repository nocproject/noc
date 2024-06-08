# optical Model Interface

Additional interface for describing optical part of transceiver

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `laser_type` | str | Laser type: FP, VCSEL, DFB | {{ no }} | {{ yes }} |
| `tx_wavelength` | int | Transmit wavelength, nm | {{ yes }} | {{ yes }} |
| `rx_wavelength` | int | Receive wavelength, nm | {{ yes }} | {{ yes }} |
| `min_tx_power` | float | Minimum transmit level, dBm | {{ no }} | {{ yes }} |
| `max_tx_power` | float | Maximum transmit level, dBm | {{ no }} | {{ yes }} |
| `min_rx_power` | float | Minimum receive level, dBm | {{ no }} | {{ yes }} |
| `max_rx_power` | float | Maximum receive level, dBm | {{ no }} | {{ yes }} |
| `min_tx_osnr` | float | Minimum transmit OSNR, dB/0.1 nm | {{ no }} | {{ yes }} |
| `max_tx_osnr` | float | Maximum transmit OSNR, dB/0.1 nm | {{ no }} | {{ yes }} |
| `min_rx_osnr` | float | Minimum receive OSNR, dB/0.1 nm | {{ no }} | {{ yes }} |
| `max_rx_osnr` | float | Maximum receive OSNR, dB/0.1 nm | {{ no }} | {{ yes }} |
| `bidi` | bool | True if singlefiber, WDM. Otherwise False | {{ yes }} | {{ yes }} |
| `xwdm` | bool | True if C/D WDM. Otherwise False | {{ yes }} | {{ yes }} |
| `distance_max` | int | Max link length, m | {{ no }} | {{ no }} |
| `bit_rate` | int | Nominal bit rate, Mb/s | {{ no }} | {{ no }} |

<!-- table end -->

Minimum receive level may be equal to receiver sensitivity.

## Examples

```json
{
  "optical": {
    "bidi": true,
    "rx_wavelength": 1550,
    "tx_wavelength": 1310
  }
}
```
