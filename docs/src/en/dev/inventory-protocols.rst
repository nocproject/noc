.. _dev-inventory-protocols:

===================
Inventory Protocols
===================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

*Inventory Protocols* are logical, electrical, optic and other conventions
between connected inventory objects. *Protocols* are necessary to put additional
constraints on object models connections. i.e. `TransEth100M` transcever
cannot be put in slot, supporting only `TransEth40G`.

.. _dev-inventory-protocols-power:

Power & Energetics
------------------

+----------+-------------------------+------------------------------------------------+
| Protocol | Description             | Variants                                       |
+==========+=========================+================================================+
| 220VAC   | 220V :term:`AC`         | * <220VAC - Power Source                       |
|          |                         | * >220VAC - Power Consumer (Power Supply Unit) |
+----------+-------------------------+------------------------------------------------+
| 110VAC   | 110V :term:`AC`         | * <110VAC - Power Source                       |
|          |                         | * >110VAC - Power Consumer (Power Supply Unit) |
+----------+-------------------------+------------------------------------------------+
| -48VDC   | -36V .. -72V :term:`DC` | * <-48VDC - Power Source                       |
|          |                         | * >-48VDC - Power Consumer (Power Supply Unit) |
+----------+-------------------------+------------------------------------------------+
| +24VDC   | +18V .. +36V :term:`DC` | * >+24VDC - Power Source                       |
|          |                         | * <+24VDC - Power Consumer (Power Supply Unit  |
+----------+-------------------------+------------------------------------------------+
| POE      | :term:`PoE`             | * <POE - PoE Source Port                       |
|          |                         | * >POE - PoE Consumer Port                     |
+----------+-------------------------+------------------------------------------------+

.. _dev-inventory-protocols-serial:

Serial
------
+----------+----------------+--------------------------------+
| Protocol | Description    | Variants                       |
+==========+================+================================+
| RS232    | :term:`RS-232` | >RS232 - DTU (console)         |
|          |                | <RS232 - DCU (terminal server) |
+----------+----------------+--------------------------------+
| RS485    | :term:`RS-485` | >RS485 - DTU                   |
|          |                | <RS485 - DCU                   |
+----------+----------------+--------------------------------+
| G703     | :term:`G.703`  | G.703                          |
+----------+----------------+--------------------------------+

.. _dev-inventory-protocols-usb:

USB
---

+----------+-------------+------------------+
| Protocol | Description | Variants         |
+==========+=============+==================+
| USB10    | USB 1.0     | >USB10 - Whistle |
|          |             | <USB10 - Hub     |
+----------+-------------+------------------+
| USB11    | USB 1.1     | >USB11 - Whistle |
|          |             | <USB11 - Hub     |
+----------+-------------+------------------+
| USB20    | USB 2.0     | >USB20 - Whistle |
|          |             | <USB20 - Hub     |
+----------+-------------+------------------+

.. _dev-inventory-protocols-transceivers:

Transceivers
------------

+--------------+---------------------------+----------------------------------------------------------+
| Protocol     | Description               | Variants                                                 |
+==============+===========================+==========================================================+
| TransEth100M | Ethernet 100M transceiver | TransEth100M - Both from linecard and transceiver module |
+--------------+---------------------------+----------------------------------------------------------+
| TransEth1G   | Ethernet 1G transceiver   | TransEth1G - Both from linecard and transceiver module   |
+--------------+---------------------------+----------------------------------------------------------+
| TransEth10G  | Ethernet 10G transceiver  | TransEth10G - Both from linecard and transceiver module  |
+--------------+---------------------------+----------------------------------------------------------+
| TransEth40G  | Ethernet 40G transceiver  | TransEth40G - Both from linecard and transceiver module  |
+--------------+---------------------------+----------------------------------------------------------+
| TransEth100G | Ethernet 100G transceiver | TransEth100G - Both from linecard and transceiver module |
+--------------+---------------------------+----------------------------------------------------------+
| TransSTM1    | STM-1 155M transceiver    | TransSTM1 - Both from linecard and transceiver module    |
+--------------+---------------------------+----------------------------------------------------------+
| TransSTM4    | STM-4 622M transceiver    | TransSTM4 - Both from linecard and transceiver module    |
+--------------+---------------------------+----------------------------------------------------------+
| TransSTM16   | STM-16 2.488G transceiver | TransSTM16 - Both from linecard and transceiver module   |
+--------------+---------------------------+----------------------------------------------------------+

.. _dev-inventory-protocols-ethernet:

Ethernet
--------

+------------------+----------------------------------------------------------------+------------------------+
| Protocol         | Description                                                    | Variants               |
+==================+================================================================+========================+
| 10BASET          | 10BASE-T, 10Mbit/s                                             | 10BASET                |
+------------------+----------------------------------------------------------------+------------------------+
| 100BASETX        | 100BASE-TX, 100Mbit/s                                          | 100BASETX              |
+------------------+----------------------------------------------------------------+------------------------+
| 1000BASET        | 1000BASE-T, 1Gbit/s                                            | 1000BASET              |
+------------------+----------------------------------------------------------------+------------------------+
| 1000BASETX       | 1000BASE-TX, 1Gbit/s. This standard has never been implemented | 1000BASETX             |
|                  | on commercially available equipment; do not use it.            |                        |
+------------------+----------------------------------------------------------------+------------------------+
| 100BASESX        | 100BASE-SX, 100Mbit/s, multimode, 850nm                        | >100BASESX - RX        |
|                  |                                                                | <100BASESX - TX        |
+------------------+----------------------------------------------------------------+------------------------+
| 100BASELX10-1310 | 100BASE-LX10, 100Mbit/s, multimode, 1310nm, basic wavelength   | >100BASELX10-1310 - RX |
|                  |                                                                | <100BASELX10-1310 - TX |
+------------------+----------------------------------------------------------------+------------------------+
| 100BASELX10-1550 | 100BASE-LX10, 100Mbit/s, multimode, 1310nm, used by 100BASE-BX | >100BASELX10-1550 - RX |
|                  |                                                                | <100BASELX10-1550 - TX |
+------------------+----------------------------------------------------------------+------------------------+
| 1000BASESX       | 1000BASE-SX, 1Gbit/s, multimode                                | >1000BASESX - RX       |
|                  |                                                                | <1000BASESX - TX       |
+------------------+----------------------------------------------------------------+------------------------+
| 1000BASELX-1310  | 1000BASE-LX, 1Gbit/s, singlemode, 1310nm, basic wavelength     | >1000BASELX-1310 - RX  |
|                  |                                                                | <1000BASELX-1310 - TX  |
+------------------+----------------------------------------------------------------+------------------------+
| 1000BASELX-1490  | 1000BASE-LX, 1Gbit/s, singlemode, 1490, used in 1000BASE-BX    | >1000BASELX-1490 - RX  |
|                  |                                                                | <1000BASELX-1490 - TX  |
+------------------+----------------------------------------------------------------+------------------------+
| 1000BASEEX-1310  | 1000BASE-EX, 1Gbit/s, singlemode, 1310nm                       | >1000BASEEX-1310 - RX  |
|                  |                                                                | <1000BASEEX-1310 - TX  |
+------------------+----------------------------------------------------------------+------------------------+
| 1000BASEZX-1550  | 1000BASE-ZX, 1Gbit/s, singlemode, 1550nm                       | ">1000BASEZX-1550 - RX |
|                  |                                                                | <1000BASEZX-1550 - TX" |
+------------------+----------------------------------------------------------------+------------------------+
| 10GBASESR        | 10GBASE-SR, 10Gbit/s, multimode                                | >10GBASESR - RX        |
|                  |                                                                | <10GBASESR - TX        |
+------------------+----------------------------------------------------------------+------------------------+
| 10GBASEUSR       | 10GBASE-USR, 10Gbit/s, multimode                               | >10GBASEUSR - RX       |
|                  |                                                                | <10GBASEUSR - TX       |
+------------------+----------------------------------------------------------------+------------------------+
| 10GBASELR-1310   | 10GBASE-LR, 10Gbit/s, singlemode, 1310nm                       | >10GBASELR-1310 - RX   |
|                  |                                                                | <10GBASELR-1310 - TX   |
+------------------+----------------------------------------------------------------+------------------------+
| 10GBASEER-1550   | 10GBASE-ER, 10Gbit/s, singlemode, 1550nm                       | >10GBASEER-1310 - RX   |
|                  |                                                                | <10GBASEER-1310 - TX   |
+------------------+----------------------------------------------------------------+------------------------+
| 10GBASEZR-1550   | 10GBASE-ZR, 10GBit/s, singlemode, 1550nm                       | >10GBASEZR-1310 - RX   |
|                  |                                                                | <10GBASEZR-1310 - TX   |
+------------------+----------------------------------------------------------------+------------------------+
| 10GBASECX4       | 10GBASE-CX4, 10GBit/s, copper                                  | 10GBASECX4             |
+------------------+----------------------------------------------------------------+------------------------+
