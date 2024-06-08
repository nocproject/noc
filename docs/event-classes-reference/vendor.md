# Vendor | *


## Vendor | Arista | EOS | VMTracer | Failed to connect to vCenter




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| Arista \| EOS \| VMTracer \| Failed to connect to vCenter](../alarm-classes-reference/vendor.md#vendor-arista-eos-vmtracer-failed-to-connect-to-vcenter) | :material-arrow-up: opening event | dispose |



## Vendor | Cisco | ASA | Network | Flow Accounting | Built Flow




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| proto | `str` | Protocol | {{ no }} |
| user | `str` | VPN User | {{ no }} |
| src_interface | `interface_name` | Source Interface | {{ no }} |
| src_ip | `ip_address` | Source IP | {{ no }} |
| src_port | `int` | Source port | {{ no }} |
| dst_interface | `interface_name` | Destination Interface | {{ no }} |
| dst_ip | `ip_address` | Destination IP | {{ no }} |
| dst_port | `int` | Destination port | {{ no }} |




## Vendor | Cisco | ASA | Network | Flow Accounting | Duplicate TCP SYN




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| src_interface | `interface_name` | Source Interface | {{ no }} |
| src_ip | `ip_address` | Source IP | {{ no }} |
| src_port | `int` | Source port | {{ no }} |
| dst_interface | `interface_name` | Destination Interface | {{ no }} |
| dst_ip | `ip_address` | Destination IP | {{ no }} |
| dst_port | `int` | Destination port | {{ no }} |




## Vendor | Cisco | ASA | Network | Flow Accounting | Teardown Flow




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| proto | `str` | Protocol | {{ no }} |
| user | `str` | VPN User | {{ no }} |
| src_interface | `interface_name` | Source Interface | {{ no }} |
| src_ip | `ip_address` | Source IP | {{ no }} |
| src_port | `int` | Source port | {{ no }} |
| dst_interface | `interface_name` | Destination Interface | {{ no }} |
| dst_ip | `ip_address` | Destination IP | {{ no }} |
| dst_port | `int` | Destination port | {{ no }} |
| bytes | `int` | Bytes count | {{ no }} |




## Vendor | Cisco | IOS | Network | Load Balance | Server Farm Degraded




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| farm | `str` | SLB server farm name | {{ yes }} |
| real | `ip_address` | Real IP | {{ yes }} |
| state | `str` | Real state | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| Cisco \| IOS \| Network \| Load Balance \| Server Farm Degraded](../alarm-classes-reference/vendor.md#vendor-cisco-ios-network-load-balance-server-farm-degraded) | :material-arrow-up: opening event | dispose |



## Vendor | Cisco | IOS | Network | Load Balance | Server Farm is Operate




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| farm | `str` | SLB server farm name | {{ yes }} |
| real | `ip_address` | Real IP | {{ yes }} |
| state | `str` | Real state | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| Cisco \| IOS \| Network \| Load Balance \| Server Farm Degraded](../alarm-classes-reference/vendor.md#vendor-cisco-ios-network-load-balance-server-farm-degraded) | :material-arrow-down: closing event | dispose |



## Vendor | Cisco | IOS | Network | Load Balance | vserver In Service




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module name | {{ yes }} |
| name | `str` | vserver name | {{ yes }} |
| farm | `str` | serverfarm name | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| Cisco \| IOS \| Network \| Load Balance \| vserver Out of Service](../alarm-classes-reference/vendor.md#vendor-cisco-ios-network-load-balance-vserver-out-of-service) | :material-arrow-down: closing event | dispose |



## Vendor | Cisco | IOS | Network | Load Balance | vserver Out of Service




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| module | `str` | Module name | {{ yes }} |
| name | `str` | vserver name | {{ yes }} |
| farm | `str` | serverfarm name | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| Cisco \| IOS \| Network \| Load Balance \| vserver Out of Service](../alarm-classes-reference/vendor.md#vendor-cisco-ios-network-load-balance-vserver-out-of-service) | :material-arrow-up: opening event | dispose |



## Vendor | Cisco | SCOS | Security | Attack | Attack Detected
<h3>Symptoms</h3>
Possible DoS/DDoS traffic from source


<h3>Probable Causes</h3>
Virus/Botnet activity or malicious actions


<h3>Recommended Actions</h3>
Negotiate the source if it is your customer, or ignore


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| from_ip | `ip_address` | From IP | {{ yes }} |
| to_ip | `ip_address` | To IP | {{ no }} |
| from_side | `str` | From Side | {{ yes }} |
| proto | `str` | Protocol | {{ yes }} |
| open_flows | `int` | Open Flows | {{ yes }} |
| suspected_flows | `int` | Suspected Flows | {{ yes }} |
| action | `str` | Action | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| Cisco \| SCOS \| Security \| Attack \| Attack Detected](../alarm-classes-reference/vendor.md#vendor-cisco-scos-security-attack-attack-detected) | :material-arrow-up: opening event | Attack Detected |



## Vendor | Cisco | SCOS | Security | Attack | End-of-attack detected




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| from_ip | `ip_address` | From IP | {{ yes }} |
| to_ip | `ip_address` | To IP | {{ no }} |
| from_side | `str` | From Side | {{ yes }} |
| proto | `str` | Protocol | {{ yes }} |
| flows | `int` | Flows | {{ yes }} |
| duration | `str` | Duration | {{ yes }} |
| action | `str` | Action | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| Cisco \| SCOS \| Security \| Attack \| Attack Detected](../alarm-classes-reference/vendor.md#vendor-cisco-scos-security-attack-attack-detected) | :material-arrow-down: closing event | Clear Attack Detected |



## Vendor | DLink | DxS | Chassis | CPU | Safeguard Engine enters EXHAUSTED mode
<h3>Symptoms</h3>
Device not responce, can not establish new connections


<h3>Probable Causes</h3>
High CPU utilization


<h3>Recommended Actions</h3>
Lower storm detect threshold, filter waste traffic on connected devices, restrict SNMP Views


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| unit | `int` | Unit number in stack | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| CPU \| CPU Exhausted](../alarm-classes-reference/chassis.md#chassis-cpu-cpu-exhausted) | :material-arrow-up: opening event | dispose |



## Vendor | DLink | DxS | Chassis | CPU | Safeguard Engine enters NORMAL mode
<h3>Symptoms</h3>
Device returned to work in normal mode




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| unit | `int` | Unit number in stack | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Chassis \| CPU \| CPU Exhausted](../alarm-classes-reference/chassis.md#chassis-cpu-cpu-exhausted) | :material-arrow-down: closing event | dispose |



## Vendor | f5 | BIGIP | Network | Load Balance | Node Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| node | `str` | IP or hostname | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Node Down](../alarm-classes-reference/vendor.md#vendor-f5-bigip-network-load-balance-node-down) | :material-arrow-up: opening event | dispose |



## Vendor | f5 | BIGIP | Network | Load Balance | Node Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| node | `str` | IP or hostname | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Node Down](../alarm-classes-reference/vendor.md#vendor-f5-bigip-network-load-balance-node-down) | :material-arrow-down: closing event | dispose |



## Vendor | f5 | BIGIP | Network | Load Balance | Service Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| node | `str` | IP or hostname | {{ yes }} |
| port | `int` | Service port | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Service Down](../alarm-classes-reference/vendor.md#vendor-f5-bigip-network-load-balance-service-down) | :material-arrow-up: opening event | dispose |



## Vendor | f5 | BIGIP | Network | Load Balance | Service Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| node | `str` | IP or hostname | {{ yes }} |
| port | `int` | Service port | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Service Down](../alarm-classes-reference/vendor.md#vendor-f5-bigip-network-load-balance-service-down) | :material-arrow-down: closing event | dispose |


