# Security


## Security | Abduct | Cable Abduct


<h3>Probable Causes</h3>
Multiple access links goes down almost in same time


<h3>Recommended Actions</h3>
Check electrics and send security team to catch the thief



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Abduct \| Cable Abduct](../event-classes-reference/security.md#security-abduct-cable-abduct) | :material-arrow-up: opening event |



## Security | Access | Case Open




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Access \| Case Close](../event-classes-reference/security.md#security-access-case-close) | :material-arrow-down: closing event |
| [Security \| Access \| Case Open](../event-classes-reference/security.md#security-access-case-open) | :material-arrow-up: opening event |



## Security | Access | Door Open




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Access \| Door Close](../event-classes-reference/security.md#security-access-door-close) | :material-arrow-down: closing event |
| [Security \| Access \| Door Open](../event-classes-reference/security.md#security-access-door-open) | :material-arrow-up: opening event |



## Security | Attack | Attack

<h3>Symptoms</h3>
Unsolicitized traffic from source


<h3>Probable Causes</h3>
Virus/Botnet activity or malicious actions


<h3>Recommended Actions</h3>
Negotiate the source if it is your customer, or ignore


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Attack name |  |
| interface | Interface |  |
| src_ip | Source IP |  |
| src_mac | Source MAC |  |
| vlan | Vlan ID |  |
| description | Interface description |  |
| vlan_name | Vlan name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Attack \| Attack](../event-classes-reference/security.md#security-attack-attack) | :material-arrow-up: opening event |



## Security | Attack | Blat Attack




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| src_ip | Source IP |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Attack \| Blat Attack](../event-classes-reference/security.md#security-attack-blat-attack) | :material-arrow-up: opening event |



## Security | Attack | IP Spoofing




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| src_ip | Source IP |  |
| src_mac | Source MAC |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Attack \| IP Spoofing](../event-classes-reference/security.md#security-attack-ip-spoofing) | :material-arrow-up: opening event |



## Security | Attack | Land Attack




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| src_ip | Source IP |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Attack \| Land Attack](../event-classes-reference/security.md#security-attack-land-attack) | :material-arrow-up: opening event |



## Security | Attack | Ping Of Death




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| src_ip | Source IP |  |
| src_mac | Source MAC |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Attack \| Ping Of Death](../event-classes-reference/security.md#security-attack-ping-of-death) | :material-arrow-up: opening event |



## Security | Attack | Smurf Attack




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| src_ip | Source IP |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Attack \| Smurf Attack](../event-classes-reference/security.md#security-attack-smurf-attack) | :material-arrow-up: opening event |



## Security | Attack | TCP SYNFIN Scan




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| src_ip | Source IP |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Attack \| TCP SYNFIN Scan](../event-classes-reference/security.md#security-attack-tcp-synfin-scan) | :material-arrow-up: opening event |



## Security | Attack | Teardrop Attack




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| src_ip | Source IP |  |
| src_mac | Source MAC |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Attack \| Teardrop Attack](../event-classes-reference/security.md#security-attack-teardrop-attack) | :material-arrow-up: opening event |



## Security | Authentication | RADIUS server failed




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| ip | RADIUS server address |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Authentication \| RADIUS server failed](../event-classes-reference/security.md#security-authentication-radius-server-failed) | :material-arrow-up: opening event |
| [Security \| Authentication \| RADIUS server recovered](../event-classes-reference/security.md#security-authentication-radius-server-recovered) | :material-arrow-down: closing event |



## Security | Authentication | TACACS+ server failed




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| ip | TACACS+ server address |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Security \| Authentication \| TACACS+ server failed](../event-classes-reference/security.md#security-authentication-tacacs+-server-failed) | :material-arrow-up: opening event |
| [Security \| Authentication \| TACACS+ server recovered](../event-classes-reference/security.md#security-authentication-tacacs+-server-recovered) | :material-arrow-down: closing event |


