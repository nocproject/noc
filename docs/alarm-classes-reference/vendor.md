# Vendor


## Vendor | Arista | EOS | VMTracer | Failed to connect to vCenter




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Vendor \| Arista \| EOS \| VMTracer \| Failed to connect to vCenter](../event-classes-reference/vendor.md#vendor-arista-eos-vmtracer-failed-to-connect-to-vcenter) | :material-arrow-up: opening event |



## Vendor | Cisco | IOS | Network | Load Balance | Server Farm Degraded




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| farm | SLB server farm name |  |
| real | Real IP |  |
| state | Real state |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Vendor \| Cisco \| IOS \| Network \| Load Balance \| Server Farm Degraded](../event-classes-reference/vendor.md#vendor-cisco-ios-network-load-balance-server-farm-degraded) | :material-arrow-up: opening event |
| [Vendor \| Cisco \| IOS \| Network \| Load Balance \| Server Farm is Operate](../event-classes-reference/vendor.md#vendor-cisco-ios-network-load-balance-server-farm-is-operate) | :material-arrow-down: closing event |



## Vendor | Cisco | IOS | Network | Load Balance | vserver Out of Service




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| module | Module name |  |
| name | vserver name |  |
| farm | serverfarm name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Vendor \| Cisco \| IOS \| Network \| Load Balance \| vserver In Service](../event-classes-reference/vendor.md#vendor-cisco-ios-network-load-balance-vserver-in-service) | :material-arrow-down: closing event |
| [Vendor \| Cisco \| IOS \| Network \| Load Balance \| vserver Out of Service](../event-classes-reference/vendor.md#vendor-cisco-ios-network-load-balance-vserver-out-of-service) | :material-arrow-up: opening event |



## Vendor | Cisco | SCOS | Security | Attack | Attack Detected

<h3>Symptoms</h3>
Possible DoS/DDoS traffic from source


<h3>Probable Causes</h3>
Virus/Botnet activity or malicious actions


<h3>Recommended Actions</h3>
Negotiate the source if it is your customer, or ignore


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| from_ip | From IP |  |
| to_ip | To IP |  |
| from_side | From Side |  |
| proto | Protocol |  |
| open_flows | Open Flows |  |
| suspected_flows | Suspected Flows |  |
| action | Action |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Vendor \| Cisco \| SCOS \| Security \| Attack \| Attack Detected](../event-classes-reference/vendor.md#vendor-cisco-scos-security-attack-attack-detected) | :material-arrow-up: opening event |
| [Vendor \| Cisco \| SCOS \| Security \| Attack \| End-of-attack detected](../event-classes-reference/vendor.md#vendor-cisco-scos-security-attack-end-of-attack-detected) | :material-arrow-down: closing event |



## Vendor | f5 | BIGIP | Network | Load Balance | Node Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| node | IP or hostname |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Node Down](../event-classes-reference/vendor.md#vendor-f5-bigip-network-load-balance-node-down) | :material-arrow-up: opening event |
| [Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Node Up](../event-classes-reference/vendor.md#vendor-f5-bigip-network-load-balance-node-up) | :material-arrow-down: closing event |



## Vendor | f5 | BIGIP | Network | Load Balance | Service Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| node | IP or hostname |  |
| port | Service port |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Service Down](../event-classes-reference/vendor.md#vendor-f5-bigip-network-load-balance-service-down) | :material-arrow-up: opening event |
| [Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Service Up](../event-classes-reference/vendor.md#vendor-f5-bigip-network-load-balance-service-up) | :material-arrow-down: closing event |


