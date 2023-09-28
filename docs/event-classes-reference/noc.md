# NOC | *


## NOC | IPAM | VRF Group Address Collision


<h3>Probable Causes</h3>
Equipment misconfiguration of IP address misallocation


<h3>Recommended Actions</h3>
Check address allocation and equipment configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| address | `str` | Address | {{ yes }} |
| vrf | `str` | VRF | {{ yes }} |
| interface | `str` | Interface | {{ no }} |
| existing_vrf | `str` | Existing VRF | {{ yes }} |
| existing_object | `str` | Existing Object | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| IPAM \| VRF Group Address Collision](../alarm-classes-reference/noc.md#noc-ipam-vrf-group-address-collision) | :material-arrow-up: opening event | dispose |



## NOC | Managed Object | Ping Failed
<h3>Symptoms</h3>
Cannot execute SA tasks on the object


<h3>Probable Causes</h3>
The object is not responding to ICMP echo-requests


<h3>Recommended Actions</h3>
Check object is alive. Check routing to this object. Check firewalls


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| Managed Object \| Ping Failed](../alarm-classes-reference/noc.md#noc-managed-object-ping-failed) | :material-arrow-up: opening event | dispose |



## NOC | Managed Object | Ping OK
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
The object is alive and responding to ICMP echo-requests


<h3>Recommended Actions</h3>
No reaction needed


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| Managed Object \| Ping Failed](../alarm-classes-reference/noc.md#noc-managed-object-ping-failed) | :material-arrow-down: closing event | dispose |
| [Chassis \| PSU \| Power Failed](../alarm-classes-reference/chassis.md#chassis-psu-power-failed) | :material-arrow-down: closing event | dispose |



## NOC | Periodic | Periodic Failed
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
Failure occured when noc-scheduler tried to execute periodic task


<h3>Recommended Actions</h3>
Check noc-scheduler, noc-sae and noc-activator logs


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| task | `str` | Task's name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| Periodic \| Periodic Failed](../alarm-classes-reference/noc.md#noc-periodic-periodic-failed) | :material-arrow-up: opening event | dispose |



## NOC | Periodic | Periodic OK
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
noc-scheduler daemon successfully completed periodic task


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| task | `str` | Task's name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| Periodic \| Periodic Failed](../alarm-classes-reference/noc.md#noc-periodic-periodic-failed) | :material-arrow-down: closing event | dispose |



## NOC | SA | Join Activator Pool
<h3>Symptoms</h3>
SA performance increased


<h3>Probable Causes</h3>
noc-activator process been launched


<h3>Recommended Actions</h3>
No recommended actions


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Activator pool name | {{ yes }} |
| instance | `str` | Activator instance | {{ yes }} |
| sessions | `int` | Instance's script sessions | {{ yes }} |
| min_members | `int` | Pool's members lower threshold | {{ yes }} |
| min_sessions | `int` | Pool's sessions lower threshold | {{ yes }} |
| pool_members | `int` | Pool's current members | {{ yes }} |
| pool_sessions | `int` | Pool's current sessions limit | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| SA \| Activator Pool Degraded](../alarm-classes-reference/noc.md#noc-sa-activator-pool-degraded) | :material-arrow-down: closing event | clear |
| [NOC \| SA \| Activator Pool Degraded](../alarm-classes-reference/noc.md#noc-sa-activator-pool-degraded) | :material-arrow-up: opening event | raise |



## NOC | SA | Leave Activator Pool
<h3>Symptoms</h3>
SA performance decreased


<h3>Probable Causes</h3>
noc-activator process been stopped


<h3>Recommended Actions</h3>
Check appropriative process


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Activator pool name | {{ yes }} |
| instance | `str` | Activator instance | {{ yes }} |
| sessions | `int` | Instance's script sessions | {{ yes }} |
| min_members | `int` | Pool's members lower threshold | {{ yes }} |
| min_sessions | `int` | Pool's sessions lower threshold | {{ yes }} |
| pool_members | `int` | Pool's current members | {{ yes }} |
| pool_sessions | `int` | Pool's current sessions limit | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [NOC \| SA \| Activator Pool Degraded](../alarm-classes-reference/noc.md#noc-sa-activator-pool-degraded) | :material-arrow-down: closing event | clear |
| [NOC \| SA \| Activator Pool Degraded](../alarm-classes-reference/noc.md#noc-sa-activator-pool-degraded) | :material-arrow-up: opening event | raise |



## NOC | Unhandled Exception
<h3>Symptoms</h3>
Unexpected behavior of NOC


<h3>Probable Causes</h3>
Bug in NOC


<h3>Recommended Actions</h3>
Grab this event, clear valuable data and submit an issue at http://nocproject.org/


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| component | `str` | NOC's component | {{ yes }} |
| traceback | `str` | Exception traceback | {{ yes }} |
| file | `str` | Failed module | {{ no }} |
| line | `int` | Failed line | {{ no }} |




## NOC | Unknown Event Source
<h3>Symptoms</h3>
Events from particular device are ignored by Fault Management


<h3>Probable Causes</h3>
Event's source address does not belong to any Managed Object's trap_source


<h3>Recommended Actions</h3>
Add appropriative Managed Object or fix trap_source


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Event SRC IP | {{ yes }} |
| collector_ip | `ip_address` | Collector's IP address | {{ yes }} |
| collector_port | `int` | Collector's port | {{ yes }} |
| activator | `str` | Activator pool | {{ yes }} |



