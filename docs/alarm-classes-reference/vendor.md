# Vendor


## Vendor | Arista | EOS | VMTracer | Failed to connect to vCenter




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| reason | Reason |  |



## Vendor | Cisco | IOS | Network | Load Balance | Server Farm Degraded




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| farm | SLB server farm name |  |
| real | Real IP |  |
| state | Real state |  |



## Vendor | Cisco | IOS | Network | Load Balance | vserver Out of Service




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| module | Module name |  |
| name | vserver name |  |
| farm | serverfarm name |  |



## Vendor | Cisco | SCOS | Security | Attack | Attack Detected

### Symptoms
Possible DoS/DDoS traffic from source


### Probable Causes
Virus/Botnet activity or malicious actions


### Recommended Actions
Negotiate the source if it is your customer, or ignore


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| from_ip | From IP |  |
| to_ip | To IP |  |
| from_side | From Side |  |
| proto | Protocol |  |
| open_flows | Open Flows |  |
| suspected_flows | Suspected Flows |  |
| action | Action |  |



## Vendor | f5 | BIGIP | Network | Load Balance | Node Down




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| node | IP or hostname |  |



## Vendor | f5 | BIGIP | Network | Load Balance | Service Down




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| node | IP or hostname |  |
| port | Service port |  |


