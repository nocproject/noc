# Security | *


## Security | ACL | ACL Deny




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | ACL Name | {{ no }} |
| proto | `str` | Protocol | {{ no }} |
| src_interface | `interface_name` | Source Interface | {{ no }} |
| src_ip | `ip_address` | Source IP | {{ no }} |
| src_port | `int` | Source port | {{ no }} |
| src_mac | `mac` | Source MAC | {{ no }} |
| dst_interface | `interface_name` | Destination Interface | {{ no }} |
| dst_ip | `ip_address` | Destination IP | {{ no }} |
| dst_port | `int` | Destination port | {{ no }} |
| count | `int` | Packets count | {{ no }} |
| flags | `str` | Flags | {{ no }} |




## Security | ACL | ACL Permit




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | ACL Name | {{ no }} |
| proto | `str` | Protocol | {{ no }} |
| src_interface | `interface_name` | Source Interface | {{ no }} |
| src_ip | `ip_address` | Source IP | {{ no }} |
| src_port | `int` | Source port | {{ no }} |
| src_mac | `mac` | Source MAC | {{ no }} |
| dst_interface | `interface_name` | Destination Interface | {{ no }} |
| dst_ip | `ip_address` | Destination IP | {{ no }} |
| dst_port | `int` | Destination port | {{ no }} |
| count | `int` | Packets count | {{ no }} |
| flags | `str` | Flags | {{ no }} |




## Security | Abduct | Cable Abduct


<h3>Probable Causes</h3>
Multiple access links goes down almost in same time


<h3>Recommended Actions</h3>
Check electrics and send security team to catch the thief


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Abduct \| Cable Abduct](../alarm-classes-reference/security.md#security-abduct-cable-abduct) | :material-arrow-up: opening event | dispose |



## Security | Access | Case Close




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Access \| Case Open](../alarm-classes-reference/security.md#security-access-case-open) | :material-arrow-down: closing event | dispose |



## Security | Access | Case Open




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Access \| Case Open](../alarm-classes-reference/security.md#security-access-case-open) | :material-arrow-up: opening event | dispose |



## Security | Access | Door Close




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Access \| Door Open](../alarm-classes-reference/security.md#security-access-door-open) | :material-arrow-down: closing event | dispose |



## Security | Access | Door Open




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Access \| Door Open](../alarm-classes-reference/security.md#security-access-door-open) | :material-arrow-up: opening event | dispose |



## Security | Accounting | WebVPN | Assigned




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| group | `str` | Group WebVPN | {{ no }} |
| user | `str` | User | {{ no }} |
| src_ip | `ip_address` | User outside IP | {{ no }} |
| dst_ip | `ipv4_address` | User inside IP | {{ no }} |
| dst_ipv6 | `ipv6_address` | User inside ipv6 | {{ no }} |




## Security | Accounting | WebVPN | Disconnected
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
Session terminated


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| group | `str` | Group WebVPN | {{ no }} |
| user | `str` | Username | {{ no }} |
| ip | `ip_address` | IP | {{ no }} |
| type | `str` | Session type | {{ no }} |
| duration | `int` | Duration | {{ no }} |
| bytes_xmt | `int` | Bytes xmt | {{ no }} |
| bytes_rcv | `int` | Bytes rcv | {{ no }} |
| reason | `str` | Reason | {{ no }} |




## Security | Attack | Attack
<h3>Symptoms</h3>
Unsolicitized traffic from source


<h3>Probable Causes</h3>
Virus/Botnet activity or malicious actions


<h3>Recommended Actions</h3>
Negotiate the source if it is your customer, or ignore


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Attack name | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |
| src_ip | `ip_address` | Source IP | {{ no }} |
| src_mac | `mac` | Source MAC | {{ no }} |
| vlan | `int` | Vlan ID | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Attack](../alarm-classes-reference/security.md#security-attack-attack) | :material-arrow-up: opening event | dispose |



## Security | Attack | Blat Attack




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Blat Attack](../alarm-classes-reference/security.md#security-attack-blat-attack) | :material-arrow-up: opening event | dispose |



## Security | Attack | IP Spoofing




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ yes }} |
| src_mac | `mac` | Source MAC | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| IP Spoofing](../alarm-classes-reference/security.md#security-attack-ip-spoofing) | :material-arrow-up: opening event | dispose |



## Security | Attack | Land Attack




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Land Attack](../alarm-classes-reference/security.md#security-attack-land-attack) | :material-arrow-up: opening event | dispose |



## Security | Attack | Ping Of Death




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ yes }} |
| src_mac | `mac` | Source MAC | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Ping Of Death](../alarm-classes-reference/security.md#security-attack-ping-of-death) | :material-arrow-up: opening event | dispose |



## Security | Attack | Smurf Attack




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Smurf Attack](../alarm-classes-reference/security.md#security-attack-smurf-attack) | :material-arrow-up: opening event | dispose |



## Security | Attack | TCP SYNFIN Scan




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| TCP SYNFIN Scan](../alarm-classes-reference/security.md#security-attack-tcp-synfin-scan) | :material-arrow-up: opening event | dispose |



## Security | Attack | Teardrop Attack




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ yes }} |
| src_mac | `mac` | Source MAC | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Teardrop Attack](../alarm-classes-reference/security.md#security-attack-teardrop-attack) | :material-arrow-up: opening event | dispose |



## Security | Audit | Clearing Counters




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface name | {{ no }} |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User IP | {{ no }} |




## Security | Audit | Command
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
Command executed by user logged by audit system


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User IP | {{ no }} |
| command | `str` | Command | {{ yes }} |




## Security | Audit | Cron
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
Command executed by cron


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| command | `str` | Command | {{ yes }} |




## Security | Authentication | 802.1x failed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | user name | {{ no }} |




## Security | Authentication | Authentication Failed
<h3>Symptoms</h3>
No specific symptoms



<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |




## Security | Authentication | Login
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
User successfully logged in


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |




## Security | Authentication | Login Failed
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
User failed to log in. Username or password mismatch


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |




## Security | Authentication | Logout
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
User successfully logged out. Session terminated


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |




## Security | Authentication | Privilege Level Change Fail
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
User privilege level changed


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |
| from_priv | `str` | Old privilegies | {{ no }} |
| to_priv | `str` | Current privilegies | {{ no }} |




## Security | Authentication | Privilege Level Changed
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
User privilege level changed


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |
| from_priv | `str` | Old privilegies | {{ no }} |
| to_priv | `str` | Current privilegies | {{ no }} |




## Security | Authentication | RADIUS server failed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | RADIUS server address | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Authentication \| RADIUS server failed](../alarm-classes-reference/security.md#security-authentication-radius-server-failed) | :material-arrow-up: opening event | dispose |



## Security | Authentication | RADIUS server recovered




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | RADIUS server address | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Authentication \| RADIUS server failed](../alarm-classes-reference/security.md#security-authentication-radius-server-failed) | :material-arrow-down: closing event | dispose |



## Security | Authentication | Rejected
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
User successfully logged out. Session terminated


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |
| server | `ip_address` | Server | {{ no }} |
| user | `str` | User | {{ no }} |
| src_ip | `ip_address` | Outside user ip | {{ no }} |




## Security | Authentication | SNMP Authentication Failure
<h3>Symptoms</h3>
NOC, NMS and monitoring systems cannot interact with the box over SNMP protocol


<h3>Probable Causes</h3>
SNMP server is misconfigured, community mismatch, misconfigured ACL or brute-force attack in progress


<h3>Recommended Actions</h3>
Check SNMP configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Request source address | {{ yes }} |
| community | `str` | Request SNMP community | {{ no }} |




## Security | Authentication | TACACS+ server failed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | TACACS+ server address | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Authentication \| TACACS+ server failed](../alarm-classes-reference/security.md#security-authentication-tacacs+-server-failed) | :material-arrow-up: opening event | dispose |



## Security | Authentication | TACACS+ server recovered




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | TACACS+ server address | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Authentication \| TACACS+ server failed](../alarm-classes-reference/security.md#security-authentication-tacacs+-server-failed) | :material-arrow-down: closing event | dispose |


