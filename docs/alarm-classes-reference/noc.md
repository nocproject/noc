# NOC


## NOC | IPAM | VRF Group Address Collision


<h3>Probable Causes</h3>
Equipment misconfiguration of IP address misallocation


<h3>Recommended Actions</h3>
Check address allocation and equipment configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| address | Address |  |
| vrf | VRF |  |
| interface | Interface |  |
| existing_vrf | Existing VRF |  |
| existing_object | Existing Object |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [NOC \| IPAM \| VRF Group Address Collision](../event-classes-reference/noc.md#noc-ipam-vrf-group-address-collision) | :material-arrow-up: opening event |



## NOC | Managed Object | Access Degraded

<h3>Symptoms</h3>
NOC cannot interact with the box


<h3>Probable Causes</h3>
Device or Access server is misconfigured, community mismatch or misconfigured ACL


<h3>Recommended Actions</h3>
Check Access configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason by access lost |  |




## NOC | Managed Object | Access Lost

<h3>Symptoms</h3>
NOC cannot interact with the box


<h3>Probable Causes</h3>
Device or Access server is misconfigured, community mismatch or misconfigured ACL


<h3>Recommended Actions</h3>
Check Access configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason by access lost |  |
| method | Method that lost access |  |




## NOC | Managed Object | Configuration Errors | Misconfigured SNMP

<h3>Symptoms</h3>
NOC cannot interact with the box over SNMP protocol


<h3>Probable Causes</h3>
SNMP server is misconfigured, community mismatch or misconfigured ACL


<h3>Recommended Actions</h3>
Check SNMP configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Request source |  |




## NOC | Managed Object | Denied Firmware


<h3>Probable Causes</h3>
Installed firmware on device is denied by system policy.


<h3>Recommended Actions</h3>
Update firmware on device.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |




## NOC | Managed Object | New Platform


<h3>Probable Causes</h3>
New Platform Creation Policy in  ManagedObject Profile deny added new platform discovered on device.


<h3>Recommended Actions</h3>
Go to menu Inventory -> Setup -> Platform, added it manually and restart discovery.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |




## NOC | Managed Object | Ping Failed

<h3>Symptoms</h3>
Cannot execute SA tasks on the object


<h3>Probable Causes</h3>
The object is not responding to ICMP echo-requests


<h3>Recommended Actions</h3>
Check object is alive. Check routing to this object. Check firewalls



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [NOC \| Managed Object \| Ping Failed](../event-classes-reference/noc.md#noc-managed-object-ping-failed) | :material-arrow-up: opening event |
| [NOC \| Managed Object \| Ping OK](../event-classes-reference/noc.md#noc-managed-object-ping-ok) | :material-arrow-down: closing event |



## NOC | PM | High Error

<h3>Symptoms</h3>
Values are out of second threshold value.


<h3>Probable Causes</h3>
Metric value cross critical threshold



<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| metric | Metric name |  |
| scope | Metric scope |  |
| path | Path to component raising alarm |  |
| labels | Metric labels |  |
| sensor | Sensor BI_ID for sensor alarm |  |
| sla_probe | SLA Probe BI_ID for SLA threshold |  |
| value | Metric value |  |
| threshold | Threshold value |  |
| window_type | Type of window (time or count) |  |
| window | Window size |  |
| window_function | Function apply to window |  |




## NOC | PM | High Warning

<h3>Symptoms</h3>
Values are out of second threshold value.


<h3>Probable Causes</h3>
Metric value cross critical threshold



<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| metric | Metric name |  |
| scope | Metric scope |  |
| path | Path to component raising alarm |  |
| labels | Metric labels |  |
| sensor | Sensor BI_ID for sensor alarm |  |
| sla_probe | SLA Probe BI_ID for SLA threshold |  |
| value | Metric value |  |
| threshold | Threshold value |  |
| window_type | Type of window (time or count) |  |
| window | Window size |  |
| window_function | Function apply to window |  |




## NOC | PM | Low Error

<h3>Symptoms</h3>
Values are out of first threshold value.




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| metric | Metric name |  |
| scope | Metric scope |  |
| path | Path to component raising alarm |  |
| labels | Metric labels |  |
| sensor | Sensor BI_ID for sensor alarm |  |
| sla_probe | SLA Probe BI_ID for SLA threshold |  |
| value | Metric value |  |
| threshold | Threshold value |  |
| window_type | Type of window (time or count) |  |
| window | Window size |  |
| window_function | Function apply to window |  |




## NOC | PM | Low Warning

<h3>Symptoms</h3>
Values are out of first threshold value.




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| metric | Metric name |  |
| scope | Metric scope |  |
| path | Path to component raising alarm |  |
| labels | Metric labels |  |
| sensor | Sensor BI_ID for sensor alarm |  |
| sla_probe | SLA Probe BI_ID for SLA threshold |  |
| value | Metric value |  |
| threshold | Threshold value |  |
| window_type | Type of window (time or count) |  |
| window | Window size |  |
| window_function | Function apply to window |  |




## NOC | PM | Out of Interface Thresholds




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | None |  |
| description | None |  |
| metric | Threshold metric |  |




## NOC | PM | Out of Thresholds




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| action | Metric Action for processed threshold |  |
| ovalue | Metric Value |  |
| rule | Metric Rule processed threshold |  |
| tvalue | Threshold |  |
| metric | Metric processed threshold |  |




## NOC | Periodic | Periodic Failed

<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
Failure occured when noc-scheduler tried to execute periodic task


<h3>Recommended Actions</h3>
Check noc-scheduler, noc-sae and noc-activator logs


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| task | Task name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [NOC \| Periodic \| Periodic Failed](../event-classes-reference/noc.md#noc-periodic-periodic-failed) | :material-arrow-up: opening event |
| [NOC \| Periodic \| Periodic OK](../event-classes-reference/noc.md#noc-periodic-periodic-ok) | :material-arrow-down: closing event |



## NOC | SA | Activator Pool Degraded

<h3>Symptoms</h3>
Cannot run SA tasks. Too many timeout errors


<h3>Probable Causes</h3>
noc-activator processes down


<h3>Recommended Actions</h3>
Check noc-activator processes. Check network connectivity


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Pool Name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [NOC \| SA \| Join Activator Pool](../event-classes-reference/noc.md#noc-sa-join-activator-pool) | :material-arrow-down: closing event |
| [NOC \| SA \| Join Activator Pool](../event-classes-reference/noc.md#noc-sa-join-activator-pool) | :material-arrow-up: opening event |
| [NOC \| SA \| Leave Activator Pool](../event-classes-reference/noc.md#noc-sa-leave-activator-pool) | :material-arrow-down: closing event |
| [NOC \| SA \| Leave Activator Pool](../event-classes-reference/noc.md#noc-sa-leave-activator-pool) | :material-arrow-up: opening event |


