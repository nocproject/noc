# nri check

Building links based on information from an external system. The integration mechanism with an external system, [Remote System](../../concepts/remote-system/index.md), allows you to extract link information and build links in NOC. To do this, implementation of extraction in the [ETL](../../etl/index.md) adapter and port mapping adapters [portmapper](../../etl/index.md#Portmapper) are required.

## Requirements

* Polling NRI and `NRI Portmapper` are enabled in the [Managed Object Profile](../../concepts/managed-object-profile/index.md#Box(Full_Polling)) profile.
* Implemented [Portmapper](../../etl/index.md#portmapper) for the external system.
