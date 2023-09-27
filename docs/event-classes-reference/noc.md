# NOC | *


## NOC | IPAM | VRF Group Address Collision


### Probable Causes
Equipment misconfiguration of IP address misallocation


### Recommended Actions
Check address allocation and equipment configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| address | `str` | Address | {{ yes }} |
| vrf | `str` | VRF | {{ yes }} |
| interface | `str` | Interface | {{ no }} |
| existing_vrf | `str` | Existing VRF | {{ yes }} |
| existing_object | `str` | Existing Object | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| IPAM \| VRF Group Address Collision](../alarm-classes-reference/noc.md#noc-ipam-vrf-group-address-collision) | :material-arrow-up: opening event | dispose |



## NOC | Managed Object | Ping Failed
### Symptoms
Cannot execute SA tasks on the object


### Probable Causes
The object is not responding to ICMP echo-requests


### Recommended Actions
Check object is alive. Check routing to this object. Check firewalls


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| Managed Object \| Ping Failed](../alarm-classes-reference/noc.md#noc-managed-object-ping-failed) | :material-arrow-up: opening event | dispose |



## NOC | Managed Object | Ping OK
### Symptoms
No specific symptoms


### Probable Causes
The object is alive and responding to ICMP echo-requests


### Recommended Actions
No reaction needed


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| Managed Object \| Ping Failed](../alarm-classes-reference/noc.md#noc-managed-object-ping-failed) | :material-arrow-down: closing event | dispose |
| [Chassis \| PSU \| Power Failed](../alarm-classes-reference/chassis.md#chassis-psu-power-failed) | :material-arrow-down: closing event | dispose |



## NOC | Periodic | Periodic Failed
### Symptoms
No specific symptoms


### Probable Causes
Failure occured when noc-scheduler tried to execute periodic task


### Recommended Actions
Check noc-scheduler, noc-sae and noc-activator logs


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| task | `str` | Task's name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| Periodic \| Periodic Failed](../alarm-classes-reference/noc.md#noc-periodic-periodic-failed) | :material-arrow-up: opening event | dispose |



## NOC | Periodic | Periodic OK
### Symptoms
No specific symptoms


### Probable Causes
noc-scheduler daemon successfully completed periodic task


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| task | `str` | Task's name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| Periodic \| Periodic Failed](../alarm-classes-reference/noc.md#noc-periodic-periodic-failed) | :material-arrow-down: closing event | dispose |



## NOC | SA | Join Activator Pool
### Symptoms
SA performance increased


### Probable Causes
noc-activator process been launched


### Recommended Actions
No recommended actions


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Activator pool name | {{ yes }} |
| instance | `str` | Activator instance | {{ yes }} |
| sessions | `int` | Instance's script sessions | {{ yes }} |
| min_members | `int` | Pool's members lower threshold | {{ yes }} |
| min_sessions | `int` | Pool's sessions lower threshold | {{ yes }} |
| pool_members | `int` | Pool's current members | {{ yes }} |
| pool_sessions | `int` | Pool's current sessions limit | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| SA \| Activator Pool Degraded](../alarm-classes-reference/noc.md#noc-sa-activator-pool-degraded) | :material-arrow-down: closing event | clear |
| [NOC \| SA \| Activator Pool Degraded](../alarm-classes-reference/noc.md#noc-sa-activator-pool-degraded) | :material-arrow-up: opening event | raise |



## NOC | SA | Leave Activator Pool
### Symptoms
SA performance decreased


### Probable Causes
noc-activator process been stopped


### Recommended Actions
Check appropriative process


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Activator pool name | {{ yes }} |
| instance | `str` | Activator instance | {{ yes }} |
| sessions | `int` | Instance's script sessions | {{ yes }} |
| min_members | `int` | Pool's members lower threshold | {{ yes }} |
| min_sessions | `int` | Pool's sessions lower threshold | {{ yes }} |
| pool_members | `int` | Pool's current members | {{ yes }} |
| pool_sessions | `int` | Pool's current sessions limit | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| SA \| Activator Pool Degraded](../alarm-classes-reference/noc.md#noc-sa-activator-pool-degraded) | :material-arrow-down: closing event | clear |
| [NOC \| SA \| Activator Pool Degraded](../alarm-classes-reference/noc.md#noc-sa-activator-pool-degraded) | :material-arrow-up: opening event | raise |



## NOC | Unhandled Exception
### Symptoms
Unexpected behavior of NOC


### Probable Causes
Bug in NOC


### Recommended Actions
Grab this event, clear valuable data and submit an issue at http://nocproject.org/


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| component | `str` | NOC's component | {{ yes }} |
| traceback | `str` | Exception traceback | {{ yes }} |
| file | `str` | Failed module | {{ no }} |
| line | `int` | Failed line | {{ no }} |




## NOC | Unknown Event Source
### Symptoms
Events from particular device are ignored by Fault Management


### Probable Causes
Event's source address does not belong to any Managed Object's trap_source


### Recommended Actions
Add appropriative Managed Object or fix trap_source


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Event SRC IP | {{ yes }} |
| collector_ip | `ip_address` | Collector's IP address | {{ yes }} |
| collector_port | `int` | Collector's port | {{ yes }} |
| activator | `str` | Activator pool | {{ yes }} |



