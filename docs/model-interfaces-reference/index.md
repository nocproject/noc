# Model Interfaces Reference

The NOC's inventory enables the storage of additional data in the Model Interfaces. 
Each Model Interface comprises attributes that convey specific physical or logical meanings. We define each Model Interface to serve a particular task, such as dimensions, weight measurements, power consumption, and more. NOC provides a wide range of built-in model interfaces, and users can create their own interfaces for their unique tasks.

This section details the Model Interfaces available in NOC, their attributes, 
and how they find application in various scenarios.

## Built-in Model Interfaces

| Model Interface             | Description                                                                    |
| --------------------------- | ------------------------------------------------------------------------------ |
| [address]()                 | External GIS system bindings                                                   |
| [agent]()                   | NOC Agent's bindings                                                           |
| [airflow](airflow.md)       | Airflow direction for cooling                                                  |
| [asset](asset.md)           | Inventory reference, asset, and serial numbers                                 |
| [caps](caps.md)             | Object's capabilities                                                          |
| [contacts](contacts.md)     | Administrative, billing and technical contacts for container (PoP, Room, Rack) |
| [container](container.md)   | Denotes object containers                                                      |
| [cpe](cpe.md)               | CPE bindings                                                                   |
| [cpu](cpu.md)               | CPU capabilities                                                               |
| [dimensions](dimensions.md) | Physical dimensions, like length, width, and height                            |
| [dwdm](dwdm.md)             | DWDM transponders capabilities                                                 |
| [geopoint](geopoint.md)     | Geographical coordinates                                                       |
| [hwlimits](hwlimits.md)     | Hardware limits of the devices                                                 |
| [length](length.md)         | Cable length                                                                   |
| [management](management.md) | Managed Object binding                                                         |
| [modbus](modbus.md)         | Modbus endpoint configuration                                                  |
| [optical](optical.md)       | Optical transceiver capabilities                                               |
| [plan](plan.md)             | Plan or scheme position                                                        |
| [pop](pop.md)               | Point of Presence capabilities                                                 |
| [power](power.md)           | Power consumption parameters                                                   |
| [rack](rack.md)             | Rack enclosures                                                                |
| [rackmount](rackmount.md)   | Rackmount equipment parameters and position                                    |
| [sector](sector.md)         | Antenna sector position                                                        |
| [splitter](splitter.md)     | Split optical/electrical input power to outputs with given gain                |
| [stack](stack.md)           | Indication of stack/virtual chassis/cluster                                    |
| [twinax](twinax.md)         | Twinax transceiver (two transceivers connected by cable in the assembly)       |
| [weight](weight.md)         | Weight properties                                                              |
