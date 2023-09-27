# Chassis | *


## Chassis | CPU | CPU Usage Above Threshold




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| cpu | `str` | CPU Name | {{ no }} |




## Chassis | CPU | CPU Usage Drops Below Threshold




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| cpu | `str` | CPU Name | {{ no }} |




## Chassis | CPU | CoPP Drop


### Probable Causes
CoPP protects control plane by dropping traffic exceeding thresholds



### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| cpu | `str` | CPU Name | {{ no }} |
| proto | `str` | Dropped packets protocol | {{ no }} |
| count | `int` | Dropped packets count | {{ no }} |




## Chassis | Clock | Clock Failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Clock Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Clock \| Clock Failed](../alarm-classes-reference/chassis.md#chassis-clock-clock-failed) | :material-arrow-up: opening event | dispose |



## Chassis | Clock | Clock Recovered




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Clock Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Clock \| Clock Failed](../alarm-classes-reference/chassis.md#chassis-clock-clock-failed) | :material-arrow-down: closing event | dispose |



## Chassis | Fabric | CRC Errors




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Farbic module | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Fabric \| CRC Errors](../alarm-classes-reference/chassis.md#chassis-fabric-crc-errors) | :material-arrow-up: opening event | dispose |



## Chassis | Fan | Fan Failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Fan Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Fan \| Fan Failed](../alarm-classes-reference/chassis.md#chassis-fan-fan-failed) | :material-arrow-up: opening event | dispose |



## Chassis | Fan | Fan Inserted




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Fan Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Fan \| Fan Removed](../alarm-classes-reference/chassis.md#chassis-fan-fan-removed) | :material-arrow-down: closing event | dispose |



## Chassis | Fan | Fan Recovered




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Fan Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Fan \| Fan Failed](../alarm-classes-reference/chassis.md#chassis-fan-fan-failed) | :material-arrow-down: closing event | dispose |



## Chassis | Fan | Fan Removed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Fan Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Fan \| Fan Removed](../alarm-classes-reference/chassis.md#chassis-fan-fan-removed) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Flash Device Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| device | `str` | Device name | {{ yes }} |
| size | `str` | Flash size | {{ yes }} |




## Chassis | Hardware | Flash Device Inserted




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| device | `str` | Device name | {{ yes }} |
| size | `str` | Flash size | {{ yes }} |




## Chassis | Hardware | Flash Device Removed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| device | `str` | Device name | {{ yes }} |




## Chassis | Hardware | Hardware Error
### Symptoms
Device becomes unstable or is not responding




### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Hardware Error](../alarm-classes-reference/chassis.md#chassis-hardware-hardware-error) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Hardware Port Error
### Symptoms
Link becomes unstable or is not responding




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Hardware port | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Hardware Port Error](../alarm-classes-reference/chassis.md#chassis-hardware-hardware-port-error) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Hardware Port Error Recover




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Hardware port | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Hardware Port Error](../alarm-classes-reference/chassis.md#chassis-hardware-hardware-port-error) | :material-arrow-down: closing event | dispose |



## Chassis | Hardware | Hardware Port Warning
### Symptoms
Link becomes unstable or is not responding




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Hardware port or slot | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Hardware Port Warning](../alarm-classes-reference/chassis.md#chassis-hardware-hardware-port-warning) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Hardware Port Warning Recover




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Hardware port or slot | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Hardware Port Warning](../alarm-classes-reference/chassis.md#chassis-hardware-hardware-port-warning) | :material-arrow-down: closing event | dispose |



## Chassis | Hardware | Hardware Warning
### Symptoms
Device becomes unstable or is not responding




### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Hardware Warning](../alarm-classes-reference/chassis.md#chassis-hardware-hardware-warning) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Module | Invalid Module




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Module \| Invalid Module](../alarm-classes-reference/chassis.md#chassis-hardware-module-invalid-module) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Module | Invalid Resume Module




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Module \| Invalid Module](../alarm-classes-reference/chassis.md#chassis-hardware-module-invalid-module) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Module | Module Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Module \| Module Down](../alarm-classes-reference/chassis.md#chassis-hardware-module-module-down) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Module | Module Error




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Module \| Module Error](../alarm-classes-reference/chassis.md#chassis-hardware-module-module-error) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Module | Module Inserted




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |




## Chassis | Hardware | Module | Module Offline




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Module \| Module Down](../alarm-classes-reference/chassis.md#chassis-hardware-module-module-down) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Module | Module Power Off




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Module \| Module Down](../alarm-classes-reference/chassis.md#chassis-hardware-module-module-down) | :material-arrow-up: opening event | dispose |



## Chassis | Hardware | Module | Module Present




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |




## Chassis | Hardware | Module | Module Removed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |




## Chassis | Hardware | Module | Module Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Hardware \| Module \| Module Down](../alarm-classes-reference/chassis.md#chassis-hardware-module-module-down) | :material-arrow-down: closing event | dispose |



## Chassis | Hardware | Module | Module not Present




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module type | {{ yes }} |
| interface | `str` | Hardware port or slot | {{ no }} |




## Chassis | Hardware | Module | Sensor Threshold Exceeded




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| tvalue | `str` | Threshold value | {{ yes }} |
| ovalue | `str` | Sensor value | {{ no }} |




## Chassis | Hardware | RF | RF Progression Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| unit | `int` | Unit number | {{ no }} |
| peer_unit | `int` | Peer unit number | {{ no }} |
| state | `str` | Unit state | {{ no }} |
| peer_state | `str` | Peer Unit state | {{ no }} |




## Chassis | Hardware | RF | RF SWACT Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| unit | `int` | Unit number | {{ yes }} |
| reason | `int` | Status Reason Code | {{ no }} |




## Chassis | Hardware | Version Upgrading




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| issu_state | `str` | The current ISSU state of the system. | {{ yes }} |
| from_version | `str` | Version from is upgrading | {{ no }} |
| to_version | `str` | Version to is upgrading | {{ no }} |
| reason | `str` | Status Reason Code | {{ no }} |




## Chassis | Linecard | LC Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| number | `str` | Slot number | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Linecard \| LC Down](../alarm-classes-reference/chassis.md#chassis-linecard-lc-down) | :material-arrow-up: opening event | dispose |



## Chassis | Linecard | LC Error




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| number | `str` | Slot number | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Linecard \| LC Error](../alarm-classes-reference/chassis.md#chassis-linecard-lc-error) | :material-arrow-up: opening event | dispose |



## Chassis | Linecard | LC Error Recover




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| number | `str` | Slot number | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Linecard \| LC Error](../alarm-classes-reference/chassis.md#chassis-linecard-lc-error) | :material-arrow-down: closing event | dispose |



## Chassis | Linecard | LC Inserted




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| number | `str` | Slot number | {{ yes }} |




## Chassis | Linecard | LC Offline




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| number | `str` | Slot number | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Linecard \| LC Down](../alarm-classes-reference/chassis.md#chassis-linecard-lc-down) | :material-arrow-up: opening event | dispose |



## Chassis | Linecard | LC Power Off




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| number | `str` | Slot number | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Linecard \| LC Down](../alarm-classes-reference/chassis.md#chassis-linecard-lc-down) | :material-arrow-up: opening event | dispose |



## Chassis | Linecard | LC Removed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| number | `str` | Slot number | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Linecard \| LC Down](../alarm-classes-reference/chassis.md#chassis-linecard-lc-down) | :material-arrow-up: opening event | dispose |



## Chassis | Linecard | LC Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| number | `str` | Slot number | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Linecard \| LC Down](../alarm-classes-reference/chassis.md#chassis-linecard-lc-down) | :material-arrow-down: closing event | dispose |



## Chassis | Linecard | Redundancy Switchover




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | The reason of the last switchover | {{ yes }} |
| description | `str` | Module switchover description | {{ no }} |
| config | `str` | Module election priority of redundancy configuration | {{ no }} |
| state | `str` | The current running state of module | {{ no }} |




## Chassis | Memory | Memory Usage Above Threshold




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| slot | `str` | Slot | {{ no }} |
| ovalue | `int` |  | {{ no }} |
| tvalue | `int` |  | {{ no }} |




## Chassis | PSU | Internal Voltage Out of Range






## Chassis | PSU | PSU Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | PSU Name | {{ yes }} |
| from_state | `str` | Prevoius state | {{ no }} |
| to_state | `str` | Current state | {{ no }} |




## Chassis | PSU | PSU Failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | PSU Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| PSU \| PSU Failed](../alarm-classes-reference/chassis.md#chassis-psu-psu-failed) | :material-arrow-up: opening event | dispose |



## Chassis | PSU | PSU Output Capacity Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | PSU Name | {{ yes }} |
| model | `str` | PSU model | {{ yes }} |
| ovalue | `int` | Capacity value | {{ yes }} |




## Chassis | PSU | PSU Recovered




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | PSU Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| PSU \| PSU Failed](../alarm-classes-reference/chassis.md#chassis-psu-psu-failed) | :material-arrow-down: closing event | dispose |



## Chassis | PSU | Power Failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| condition | `str` | Condition | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| PSU \| Power Failed](../alarm-classes-reference/chassis.md#chassis-psu-power-failed) | :material-arrow-up: opening event | dispose |



## Chassis | RAM | Insufficient Memory




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| RAM \| Insufficient Memory](../alarm-classes-reference/chassis.md#chassis-ram-insufficient-memory) | :material-arrow-up: opening event | dispose |



## Chassis | RAM | Memory Buffer Peak




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| buffer | `str` | Buffer name | {{ yes }} |
| ovalue | `int` | Buffer value | {{ yes }} |




## Chassis | RAM | RAM Failed
### Symptoms
From random instability to complete operation failure



### Recommended Actions
Replace faulty RAM module


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| bank | `str` | Bank Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| RAM \| RAM Failed](../alarm-classes-reference/chassis.md#chassis-ram-ram-failed) | :material-arrow-up: opening event | dispose |



## Chassis | Stack | Stack Degraded




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| unit | `int` | Unit number | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Stack \| Stack Degraded](../alarm-classes-reference/chassis.md#chassis-stack-stack-degraded) | :material-arrow-up: opening event | dispose |



## Chassis | Stack | Stack is Raised




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| unit | `int` | Unit number | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Stack \| Stack Degraded](../alarm-classes-reference/chassis.md#chassis-stack-stack-degraded) | :material-arrow-down: closing event | dispose |



## Chassis | Supervisor | Supervisor Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Supervisor name | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Supervisor \| Supervisor Down](../alarm-classes-reference/chassis.md#chassis-supervisor-supervisor-down) | :material-arrow-up: opening event | dispose |



## Chassis | Supervisor | Supervisor Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Supervisor name | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| Supervisor \| Supervisor Down](../alarm-classes-reference/chassis.md#chassis-supervisor-supervisor-down) | :material-arrow-down: closing event | dispose |



## Chassis | TCAM | TCAM Entry Capacity Exceeded




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| TCAM \| TCAM Entry Capacity Exceeded](../alarm-classes-reference/chassis.md#chassis-tcam-tcam-entry-capacity-exceeded) | :material-arrow-up: opening event | dispose |



## Chassis | TCAM | TCAM Error
### Symptoms
From random instability to complete operation failure




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| TCAM \| TCAM Error](../alarm-classes-reference/chassis.md#chassis-tcam-tcam-error) | :material-arrow-up: opening event | dispose |


