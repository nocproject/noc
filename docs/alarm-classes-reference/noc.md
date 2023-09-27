# NOC


## NOC | IPAM | VRF Group Address Collision


### Probable Causes
Equipment misconfiguration of IP address misallocation


### Recommended Actions
Check address allocation and equipment configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| address | Address |  |
| vrf | VRF |  |
| interface | Interface |  |
| existing_vrf | Existing VRF |  |
| existing_object | Existing Object |  |



## NOC | Managed Object | Access Degraded

### Symptoms
NOC cannot interact with the box


### Probable Causes
Device or Access server is misconfigured, community mismatch or misconfigured ACL


### Recommended Actions
Check Access configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason by access lost |  |



## NOC | Managed Object | Access Lost

### Symptoms
NOC cannot interact with the box


### Probable Causes
Device or Access server is misconfigured, community mismatch or misconfigured ACL


### Recommended Actions
Check Access configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason by access lost |  |
| method | Method that lost access |  |



## NOC | Managed Object | Configuration Errors | Misconfigured SNMP

### Symptoms
NOC cannot interact with the box over SNMP protocol


### Probable Causes
SNMP server is misconfigured, community mismatch or misconfigured ACL


### Recommended Actions
Check SNMP configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Request source |  |



## NOC | Managed Object | Denied Firmware


### Probable Causes
Installed firmware on device is denied by system policy.


### Recommended Actions
Update firmware on device.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |



## NOC | Managed Object | New Platform


### Probable Causes
New Platform Creation Policy in  ManagedObject Profile deny added new platform discovered on device.


### Recommended Actions
Go to menu Inventory -> Setup -> Platform, added it manually and restart discovery.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |



## NOC | Managed Object | Ping Failed

### Symptoms
Cannot execute SA tasks on the object


### Probable Causes
The object is not responding to ICMP echo-requests


### Recommended Actions
Check object is alive. Check routing to this object. Check firewalls



## NOC | PM | High Error

### Symptoms
Values are out of second threshold value.


### Probable Causes
Metric value cross critical threshold



### Variables
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

### Symptoms
Values are out of second threshold value.


### Probable Causes
Metric value cross critical threshold



### Variables
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

### Symptoms
Values are out of first threshold value.




### Variables
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

### Symptoms
Values are out of first threshold value.




### Variables
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




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | None |  |
| description | None |  |
| metric | Threshold metric |  |



## NOC | PM | Out of Thresholds




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| action | Metric Action for processed threshold |  |
| ovalue | Metric Value |  |
| rule | Metric Rule processed threshold |  |
| tvalue | Threshold |  |
| metric | Metric processed threshold |  |



## NOC | Periodic | Periodic Failed

### Symptoms
No specific symptoms


### Probable Causes
Failure occured when noc-scheduler tried to execute periodic task


### Recommended Actions
Check noc-scheduler, noc-sae and noc-activator logs


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| task | Task name |  |



## NOC | SA | Activator Pool Degraded

### Symptoms
Cannot run SA tasks. Too many timeout errors


### Probable Causes
noc-activator processes down


### Recommended Actions
Check noc-activator processes. Check network connectivity


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| name | Pool Name |  |


