# Chassis


## Chassis | CPU | CPU Exhausted

<h3>Symptoms</h3>
Device not responce, can not establish new connections


<h3>Probable Causes</h3>
High CPU utilization


<h3>Recommended Actions</h3>
Lower storm detect threshold, filter waste traffic on connected devices, restrict SNMP Views



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Vendor \| DLink \| DxS \| Chassis \| CPU \| Safeguard Engine enters EXHAUSTED mode](../event-classes-reference/vendor.md#vendor-dlink-dxs-chassis-cpu-safeguard-engine-enters-exhausted-mode) | :material-arrow-up: opening event |
| [Vendor \| DLink \| DxS \| Chassis \| CPU \| Safeguard Engine enters NORMAL mode](../event-classes-reference/vendor.md#vendor-dlink-dxs-chassis-cpu-safeguard-engine-enters-normal-mode) | :material-arrow-down: closing event |



## Chassis | Clock | Clock Failed




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Clock Name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Clock \| Clock Failed](../event-classes-reference/chassis.md#chassis-clock-clock-failed) | :material-arrow-up: opening event |
| [Chassis \| Clock \| Clock Recovered](../event-classes-reference/chassis.md#chassis-clock-clock-recovered) | :material-arrow-down: closing event |



## Chassis | Fabric | CRC Errors




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Fabric Module |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Fabric \| CRC Errors](../event-classes-reference/chassis.md#chassis-fabric-crc-errors) | :material-arrow-up: opening event |



## Chassis | Fan | Fan Failed




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Fan Name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Fan \| Fan Failed](../event-classes-reference/chassis.md#chassis-fan-fan-failed) | :material-arrow-up: opening event |
| [Chassis \| Fan \| Fan Recovered](../event-classes-reference/chassis.md#chassis-fan-fan-recovered) | :material-arrow-down: closing event |



## Chassis | Fan | Fan Removed




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Fan Name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Fan \| Fan Inserted](../event-classes-reference/chassis.md#chassis-fan-fan-inserted) | :material-arrow-down: closing event |
| [Chassis \| Fan \| Fan Removed](../event-classes-reference/chassis.md#chassis-fan-fan-removed) | :material-arrow-up: opening event |



## Chassis | Hardware | Hardware Error

<h3>Symptoms</h3>
Device becomes unstable or is not responding





<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Hardware \| Hardware Error](../event-classes-reference/chassis.md#chassis-hardware-hardware-error) | :material-arrow-up: opening event |



## Chassis | Hardware | Hardware Port Error

<h3>Symptoms</h3>
Link becomes unstable or is not responding




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Hardware port |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Hardware \| Hardware Port Error](../event-classes-reference/chassis.md#chassis-hardware-hardware-port-error) | :material-arrow-up: opening event |
| [Chassis \| Hardware \| Hardware Port Error Recover](../event-classes-reference/chassis.md#chassis-hardware-hardware-port-error-recover) | :material-arrow-down: closing event |



## Chassis | Hardware | Hardware Port Warning

<h3>Symptoms</h3>
Link becomes unstable or is not responding




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Hardware port or slot |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Hardware \| Hardware Port Warning](../event-classes-reference/chassis.md#chassis-hardware-hardware-port-warning) | :material-arrow-up: opening event |
| [Chassis \| Hardware \| Hardware Port Warning Recover](../event-classes-reference/chassis.md#chassis-hardware-hardware-port-warning-recover) | :material-arrow-down: closing event |



## Chassis | Hardware | Hardware Warning

<h3>Symptoms</h3>
Device becomes unstable or is not responding





<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Hardware \| Hardware Warning](../event-classes-reference/chassis.md#chassis-hardware-hardware-warning) | :material-arrow-up: opening event |



## Chassis | Hardware | Module | Invalid Module




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| module | Module type |  |
| interface | Hardware port or slot |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Hardware \| Module \| Invalid Module](../event-classes-reference/chassis.md#chassis-hardware-module-invalid-module) | :material-arrow-up: opening event |
| [Chassis \| Hardware \| Module \| Invalid Resume Module](../event-classes-reference/chassis.md#chassis-hardware-module-invalid-resume-module) | :material-arrow-up: opening event |



## Chassis | Hardware | Module | Module Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| module | Module type |  |
| interface | Hardware port or slot |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Hardware \| Module \| Module Down](../event-classes-reference/chassis.md#chassis-hardware-module-module-down) | :material-arrow-up: opening event |
| [Chassis \| Hardware \| Module \| Module Offline](../event-classes-reference/chassis.md#chassis-hardware-module-module-offline) | :material-arrow-up: opening event |
| [Chassis \| Hardware \| Module \| Module Power Off](../event-classes-reference/chassis.md#chassis-hardware-module-module-power-off) | :material-arrow-up: opening event |
| [Chassis \| Hardware \| Module \| Module Up](../event-classes-reference/chassis.md#chassis-hardware-module-module-up) | :material-arrow-down: closing event |



## Chassis | Hardware | Module | Module Error




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| module | Module type |  |
| interface | Hardware port or slot |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Hardware \| Module \| Module Error](../event-classes-reference/chassis.md#chassis-hardware-module-module-error) | :material-arrow-up: opening event |



## Chassis | Linecard | LC Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| number | Slot number |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Linecard \| LC Down](../event-classes-reference/chassis.md#chassis-linecard-lc-down) | :material-arrow-up: opening event |
| [Chassis \| Linecard \| LC Offline](../event-classes-reference/chassis.md#chassis-linecard-lc-offline) | :material-arrow-up: opening event |
| [Chassis \| Linecard \| LC Power Off](../event-classes-reference/chassis.md#chassis-linecard-lc-power-off) | :material-arrow-up: opening event |
| [Chassis \| Linecard \| LC Removed](../event-classes-reference/chassis.md#chassis-linecard-lc-removed) | :material-arrow-up: opening event |
| [Chassis \| Linecard \| LC Up](../event-classes-reference/chassis.md#chassis-linecard-lc-up) | :material-arrow-down: closing event |



## Chassis | Linecard | LC Error




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| number | Slot number |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Linecard \| LC Error](../event-classes-reference/chassis.md#chassis-linecard-lc-error) | :material-arrow-up: opening event |
| [Chassis \| Linecard \| LC Error Recover](../event-classes-reference/chassis.md#chassis-linecard-lc-error-recover) | :material-arrow-down: closing event |



## Chassis | PSU | PSU Failed




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | PSU Name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| PSU \| PSU Failed](../event-classes-reference/chassis.md#chassis-psu-psu-failed) | :material-arrow-up: opening event |
| [Chassis \| PSU \| PSU Recovered](../event-classes-reference/chassis.md#chassis-psu-psu-recovered) | :material-arrow-down: closing event |



## Chassis | PSU | Power Failed




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| condition | Condition |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| PSU \| Power Failed](../event-classes-reference/chassis.md#chassis-psu-power-failed) | :material-arrow-up: opening event |
| [NOC \| Managed Object \| Ping OK](../event-classes-reference/noc.md#noc-managed-object-ping-ok) | :material-arrow-down: closing event |



## Chassis | RAM | Insufficient Memory




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| RAM \| Insufficient Memory](../event-classes-reference/chassis.md#chassis-ram-insufficient-memory) | :material-arrow-up: opening event |



## Chassis | RAM | RAM Failed

<h3>Symptoms</h3>
From random instability to complete operation failure



<h3>Recommended Actions</h3>
Replace faulty RAM module


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| bank | Bank Name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| RAM \| RAM Failed](../event-classes-reference/chassis.md#chassis-ram-ram-failed) | :material-arrow-up: opening event |



## Chassis | Stack | Stack Degraded




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| unit | Unit number |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Stack \| Stack Degraded](../event-classes-reference/chassis.md#chassis-stack-stack-degraded) | :material-arrow-up: opening event |
| [Chassis \| Stack \| Stack is Raised](../event-classes-reference/chassis.md#chassis-stack-stack-is-raised) | :material-arrow-down: closing event |



## Chassis | Supervisor | Supervisor Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Supervisor name |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| Supervisor \| Supervisor Down](../event-classes-reference/chassis.md#chassis-supervisor-supervisor-down) | :material-arrow-up: opening event |
| [Chassis \| Supervisor \| Supervisor Up](../event-classes-reference/chassis.md#chassis-supervisor-supervisor-up) | :material-arrow-down: closing event |



## Chassis | TCAM | TCAM Entry Capacity Exceeded




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| TCAM \| TCAM Entry Capacity Exceeded](../event-classes-reference/chassis.md#chassis-tcam-tcam-entry-capacity-exceeded) | :material-arrow-up: opening event |



## Chassis | TCAM | TCAM Error

<h3>Symptoms</h3>
From random instability to complete operation failure




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Chassis \| TCAM \| TCAM Error](../event-classes-reference/chassis.md#chassis-tcam-tcam-error) | :material-arrow-up: opening event |


