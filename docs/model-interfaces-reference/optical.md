# optical Model Interface

Additional interface for describing optical part of transceiver

## Variables

| Name          | Type  | Description                               | Required  | Constant  | Default |
| ------------- | ----- | ----------------------------------------- | --------- | --------- | ------- |
| laser_type    | str   | Laser type: FP, VCSEL, DFB                | {{ no }}  | {{ yes }} |         |
| tx_wavelength | int   | Transmit wavelength, nm                   | {{ yes }} | {{ yes }} | false   |
| rx_wavelength | int   | Receive wavelength, nm                    | {{ yes }} | {{ yes }} | false   |
| min_tx_power  | float | Minimum transmit level, dBm               | {{ no }}  | {{ yes }} | false   |
| max_tx_power  | float | Maximum transmit level, dBm               | {{ no }}  | {{ yes }} | false   |
| min_rx_power  | float | Minimum receive level, dBm                | {{ no }}  | {{ yes }} | false   |
| max_rx_power  | float | Maximum receive level, dBm                | {{ no }}  | {{ yes }} | false   |
| bidi          | bool  | True if singlefiber, WDM. Otherwise False | {{ yes }} | {{ yes }} | false   |
| min_tx_osnr   | float | Minimum transmit OSNR, dB/0.1 nm | {{ no }} | {{ yes }} | |
| max_tx_osnr   | float | Maximum transmit OSNR, dB/0.1 nm | {{ no }} | {{ yes }} | |
| min_rx_osnr   | float | Minimum receive OSNR, dB/0.1 nm | {{ no }} | {{ yes }} | |
| max_rx_osnr   | float | Maximum receive OSNR, dB/0.1 nm | {{ no }} | {{ yes }} | |
| xwdm          | bool  | True if C/D WDM. Otherwise False | {{ yes }} | {{ yes }} | false |
| distance_max  | int   | Max link length, m | {{ no }} | {{ no }} | | 
| bit_rate      | int   | Nominal bit rate, Mb/s | {{ no }} | {{ no }} | |

Minimum receive level maybe equal to receiver sensitivity.

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
