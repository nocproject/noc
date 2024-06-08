# Inventory Protocols

`Inventory Protocols` are logical, electrical, optic and other conventions
between connected inventory objects. `Protocols` are necessary to put additional
constraints on object models connections. i.e. `TransEth100M` transcever
cannot be put in slot, supporting only `TransEth40G`.

## Power & Energetics

| Protocol | Description                                | Variants                                       |
| -------- | ------------------------------------------ | ---------------------------------------------- |
| `220VAC` | 220V [AC](../glossary/index.md#ac)         | `<220VAC` - Power Source                       |
|          |                                            | `>220VAC` - Power Consumer (Power Supply Unit) |
| `110VAC` | 110V [AC](../glossary/index.md#ac)         | `<110VAC` - Power Source                       |
|          |                                            | `>110VAC` - Power Consumer (Power Supply Unit) |
| `-48VDC` | -36V .. -72V [DC](../glossary/index.md#dc) | `<-48VDC` - Power Source                       |
|          |                                            | `>-48VDC` - Power Consumer (Power Supply Unit) |
| `+24VDC` | +18V .. +36V [DC](../glossary/index.md#dc) | `>+24VDC` - Power Source                       |
|          |                                            | `<+24VDC` - Power Consumer (Power Supply Unit  |
| `POE`    | [PoE](../glossary/index.md#poe)            | `<POE` - PoE Source Port                       |
|          |                                            | `>POE` - PoE Consumer Port                     |

## Serial

| Protocol | Description                           | Variants                         |
| -------- | ------------------------------------- | -------------------------------- |
| `RS232`  | [RS-232](../glossary/index.md#rs-232) | `>RS232` - DTU (console)         |
|          |                                       | `<RS232` - DCU (terminal server) |
| `RS485`  | [RS-485](../glossary/index.md#rs-485) | `>RS485` - Slave                 |
|          |                                       | `<RS485` - Master                |
|          |                                       | `>RS485-A` - Signal-A slave      |
|          |                                       | `<RS485-A` - Signal-A master     |
|          |                                       | `>RS485-B` - Signal-B slave      |
|          |                                       | `<RS485-B` - Signal-B master     |
| `G703`   | [G.703](../glossary/index.md#g-703)   | `G.703`                          |

## USB

| Protocol | Description | Variants           |
| -------- | ----------- | ------------------ |
| `USB10`  | USB 1.0     | `>USB10` - Whistle |
|          |             | `<USB10` - Hub     |
| `USB11`  | USB 1.1     | `>USB11` - Whistle |
|          |             | `<USB11` - Hub     |
| `USB20`  | USB 2.0     | `>USB20` - Whistle |
|          |             | `<USB20` - Hub     |

## Transceivers

| Protocol       | Description               | Variants                                                   |
| -------------- | ------------------------- | ---------------------------------------------------------- |
| `TransEth100M` | Ethernet 100M transceiver | `TransEth100M` - Both from linecard and transceiver module |
| `TransEth1G`   | Ethernet 1G transceiver   | `TransEth1G` - Both from linecard and transceiver module   |
| `TransEth10G`  | Ethernet 10G transceiver  | `TransEth10G` - Both from linecard and transceiver module  |
| `TransEth40G`  | Ethernet 40G transceiver  | `TransEth40G` - Both from linecard and transceiver module  |
| `TransEth100G` | Ethernet 100G transceiver | `TransEth100G` - Both from linecard and transceiver module |
| `TransSTM1`    | STM-1 155M transceiver    | `TransSTM1` - Both from linecard and transceiver module    |
| `TransSTM4`    | STM-4 622M transceiver    | `TransSTM4` - Both from linecard and transceiver module    |
| `TransSTM16`   | STM-16 2.488G transceiver | `TransSTM16` - Both from linecard and transceiver module   |

## Ethernet

| Protocol           | Description                                                    | Variants                 |
| ------------------ | -------------------------------------------------------------- | ------------------------ |
| `10BASET`          | 10BASE-T, 10Mbit/s                                             | `10BASET`                |
| `100BASETX`        | 100BASE-TX, 100Mbit/s                                          | `100BASETX`              |
| `1000BASET`        | 1000BASE-T, 1Gbit/s                                            | `1000BASET`              |
| `1000BASETX`       | 1000BASE-TX, 1Gbit/s. This standard has never been implemented | `1000BASETX`             |
|                    | on commercially available equipment; do not use it.            |                          |
| `2.5GBASET`        | 2.5GBASE-T, 2.5Gbit/s                                          | `2.5GBASET`              |
| `5GBASET`          | 5GBASE-T, 5Gbit/s                                              | `5GBASET`                |
| `100BASESX`        | 100BASE-SX, 100Mbit/s, multimode, 850nm                        | `>100BASESX` - RX        |
|                    |                                                                | `<100BASESX` - TX        |
| `100BASELX10-1310` | 100BASE-LX10, 100Mbit/s, multimode, 1310nm, basic wavelength   | `>100BASELX10-1310` - RX |
|                    |                                                                | `<100BASELX10-1310` - TX |
| `100BASELX10-1550` | 100BASE-LX10, 100Mbit/s, multimode, 1310nm, used by 100BASE-BX | `>100BASELX10-1550` - RX |
|                    |                                                                | `<100BASELX10-1550` - TX |
| `1000BASESX`       | 1000BASE-SX, 1Gbit/s, multimode                                | `>1000BASESX` - RX       |
|                    |                                                                | `<1000BASESX` - TX       |
| `1000BASELX-1310`  | 1000BASE-LX, 1Gbit/s, singlemode, 1310nm, basic wavelength     | `>1000BASELX-1310` - RX  |
|                    |                                                                | `<1000BASELX-1310` - TX  |
| `1000BASELX-1490`  | 1000BASE-LX, 1Gbit/s, singlemode, 1490, used in 1000BASE-BX    | `>1000BASELX-1490` - RX  |
|                    |                                                                | `<1000BASELX-1490` - TX  |
| `1000BASEEX-1310`  | 1000BASE-EX, 1Gbit/s, singlemode, 1310nm                       | `>1000BASEEX-1310` - RX  |
|                    |                                                                | `<1000BASEEX-1310` - TX  |
| `1000BASEZX-1550`  | 1000BASE-ZX, 1Gbit/s, singlemode, 1550nm                       | `>1000BASEZX-1550` - RX  |
|                    |                                                                | `<1000BASEZX-1550` - TX" |
| `10GBASESR`        | 10GBASE-SR, 10Gbit/s, multimode                                | `>10GBASESR` - RX        |
|                    |                                                                | `<10GBASESR` - TX        |
| `10GBASEUSR`       | 10GBASE-USR, 10Gbit/s, multimode                               | `>10GBASEUSR` - RX       |
|                    |                                                                | `<10GBASEUSR` - TX       |
| `10GBASELR-1310`   | 10GBASE-LR, 10Gbit/s, singlemode, 1310nm                       | `>10GBASELR-1310` - RX   |
|                    |                                                                | `<10GBASELR-1310` - TX   |
| `10GBASEER-1550`   | 10GBASE-ER, 10Gbit/s, singlemode, 1550nm                       | `>10GBASEER-1310` - RX   |
|                    |                                                                | `<10GBASEER-1310` - TX   |
| `10GBASEZR-1550`   | 10GBASE-ZR, 10GBit/s, singlemode, 1550nm                       | `>10GBASEZR-1310` - RX   |
|                    |                                                                | `<10GBASEZR-1310` - TX   |
| `10GBASECX4`       | 10GBASE-CX4, 10GBit/s, copper                                  | `10GBASECX4`             |
