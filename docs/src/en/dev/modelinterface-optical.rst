.. _dev-modelinterface-optical:

=====================
optical Model Interface
=====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Additional interface for describing optical part of transceiver

Variables
---------

+---------------+--------+-----------------------------------------------+------------+------------+-----------+
| Name          | Type   | Description                                   | Required   | Constant   | Default   |
+===============+========+===============================================+============+============+===========+
| laser_type    | str    | Laser type: FP, VCSEL, DFB                    | False      | True       |           |
+---------------+--------+-----------------------------------------------+------------+------------+-----------+
| tx_wavelength | int    | Transmit wavelength, nm                       | True       | True       | false     |
+---------------+--------+-----------------------------------------------+------------+------------+-----------+
| rx_wavelength | int    | Receive wavelength, nm                        | True       | True       | false     |
+---------------+--------+-----------------------------------------------+------------+------------+-----------+
| min_tx_power  | float  | Minimum transmit level, dBm                   | False      | True       | false     |
+---------------+--------+-----------------------------------------------+------------+------------+-----------+
| max_tx_power  | float  | Maximum transmit level, dBm                   | False      | True       | false     |
+---------------+--------+-----------------------------------------------+------------+------------+-----------+
| min_rx_power  | float  | Minimum receive level, dBm                    | False      | True       | false     |
+---------------+--------+-----------------------------------------------+------------+------------+-----------+
| max_rx_power  | float  | Maximum receive level, dBm                    | False      | True       | false     |
+---------------+--------+-----------------------------------------------+------------+------------+-----------+
| bidi          | bool   | True if singlefiber, WDM. Otherwise False     | True       | True       | false     |
+---------------+--------+-----------------------------------------------+------------+------------+-----------+

Minimum receive level maybe equal to receiver sensitivity.

Examples
--------

::

    "optical": {
        "bidi": true,
        "rx_wavelength": 1550,
        "tx_wavelength": 1310
    }
