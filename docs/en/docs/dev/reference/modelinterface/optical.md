---
1ebf0a6a-5809-4c21-bae8-d93317763f25
---

# optical Model Interface

Additional interface for describing optical part of transceiver

## Variables

| Name          | Type   | Description                                   | Required         | Constant         | Default   |
| ------------- | ------ | ----------------------------------------------| ---------------- | ---------------- | --------- |
| laser_type    | str    | Laser type: FP, VCSEL, DFB                    | {{ no }} | {{ yes }} |           |
| tx_wavelength | int    | Transmit wavelength, nm                       | {{ yes }} | {{ yes }} | false     |
| rx_wavelength | int    | Receive wavelength, nm                        | {{ yes }} | {{ yes }} | false     |
| min_tx_power  | float  | Minimum transmit level, dBm                   | {{ no }} | {{ yes }} | false     |
| max_tx_power  | float  | Maximum transmit level, dBm                   | {{ no }} | {{ yes }} | false     |
| min_rx_power  | float  | Minimum receive level, dBm                    | {{ no }} | {{ yes }} | false     |
| max_rx_power  | float  | Maximum receive level, dBm                    | {{ no }} | {{ yes }} | false     |
| bidi          | bool   | True if singlefiber, WDM. Otherwise False     | {{ yes }} | {{ yes }} | false     |

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
