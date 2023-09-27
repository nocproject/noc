# Security | *


## Security | ACL | ACL Deny




### Variables
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




### Variables
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


### Probable Causes
Multiple access links goes down almost in same time


### Recommended Actions
Check electrics and send security team to catch the thief


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Abduct \| Cable Abduct](../alarm-classes-reference/security.md#security-abduct-cable-abduct) | :material-arrow-up: opening event | dispose |



## Security | Access | Case Close




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Access \| Case Open](../alarm-classes-reference/security.md#security-access-case-open) | :material-arrow-down: closing event | dispose |



## Security | Access | Case Open




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Access \| Case Open](../alarm-classes-reference/security.md#security-access-case-open) | :material-arrow-up: opening event | dispose |



## Security | Access | Door Close




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Access \| Door Open](../alarm-classes-reference/security.md#security-access-door-open) | :material-arrow-down: closing event | dispose |



## Security | Access | Door Open




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Access \| Door Open](../alarm-classes-reference/security.md#security-access-door-open) | :material-arrow-up: opening event | dispose |



## Security | Accounting | WebVPN | Assigned




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| group | `str` | Group WebVPN | {{ no }} |
| user | `str` | User | {{ no }} |
| src_ip | `ip_address` | User outside IP | {{ no }} |
| dst_ip | `ipv4_address` | User inside IP | {{ no }} |
| dst_ipv6 | `ipv6_address` | User inside ipv6 | {{ no }} |




## Security | Accounting | WebVPN | Disconnected
### Symptoms
No specific symptoms


### Probable Causes
Session terminated


### Recommended Actions
No reaction needed


### Variables
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
### Symptoms
Unsolicitized traffic from source


### Probable Causes
Virus/Botnet activity or malicious actions


### Recommended Actions
Negotiate the source if it is your customer, or ignore


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Attack name | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |
| src_ip | `ip_address` | Source IP | {{ no }} |
| src_mac | `mac` | Source MAC | {{ no }} |
| vlan | `int` | Vlan ID | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Attack](../alarm-classes-reference/security.md#security-attack-attack) | :material-arrow-up: opening event | dispose |



## Security | Attack | Blat Attack




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Blat Attack](../alarm-classes-reference/security.md#security-attack-blat-attack) | :material-arrow-up: opening event | dispose |



## Security | Attack | IP Spoofing




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ yes }} |
| src_mac | `mac` | Source MAC | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| IP Spoofing](../alarm-classes-reference/security.md#security-attack-ip-spoofing) | :material-arrow-up: opening event | dispose |



## Security | Attack | Land Attack




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Land Attack](../alarm-classes-reference/security.md#security-attack-land-attack) | :material-arrow-up: opening event | dispose |



## Security | Attack | Ping Of Death




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ yes }} |
| src_mac | `mac` | Source MAC | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Ping Of Death](../alarm-classes-reference/security.md#security-attack-ping-of-death) | :material-arrow-up: opening event | dispose |



## Security | Attack | Smurf Attack




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Smurf Attack](../alarm-classes-reference/security.md#security-attack-smurf-attack) | :material-arrow-up: opening event | dispose |



## Security | Attack | TCP SYNFIN Scan




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| TCP SYNFIN Scan](../alarm-classes-reference/security.md#security-attack-tcp-synfin-scan) | :material-arrow-up: opening event | dispose |



## Security | Attack | Teardrop Attack




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| src_ip | `ip_address` | Source IP | {{ yes }} |
| src_mac | `mac` | Source MAC | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Attack \| Teardrop Attack](../alarm-classes-reference/security.md#security-attack-teardrop-attack) | :material-arrow-up: opening event | dispose |



## Security | Audit | Clearing Counters




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface name | {{ no }} |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User IP | {{ no }} |




## Security | Audit | Command
### Symptoms
No specific symptoms


### Probable Causes
Command executed by user logged by audit system


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User IP | {{ no }} |
| command | `str` | Command | {{ yes }} |




## Security | Audit | Cron
### Symptoms
No specific symptoms


### Probable Causes
Command executed by cron


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| command | `str` | Command | {{ yes }} |




## Security | Authentication | 802.1x failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | user name | {{ no }} |




## Security | Authentication | Authentication Failed
### Symptoms
No specific symptoms



### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |




## Security | Authentication | Login
### Symptoms
No specific symptoms


### Probable Causes
User successfully logged in


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |




## Security | Authentication | Login Failed
### Symptoms
No specific symptoms


### Probable Causes
User failed to log in. Username or password mismatch


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |




## Security | Authentication | Logout
### Symptoms
No specific symptoms


### Probable Causes
User successfully logged out. Session terminated


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |




## Security | Authentication | Privilege Level Change Fail
### Symptoms
No specific symptoms


### Probable Causes
User privilege level changed


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |
| from_priv | `str` | Old privilegies | {{ no }} |
| to_priv | `str` | Current privilegies | {{ no }} |




## Security | Authentication | Privilege Level Changed
### Symptoms
No specific symptoms


### Probable Causes
User privilege level changed


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | User | {{ no }} |
| ip | `ip_address` | User address | {{ no }} |
| from_priv | `str` | Old privilegies | {{ no }} |
| to_priv | `str` | Current privilegies | {{ no }} |




## Security | Authentication | RADIUS server failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | RADIUS server address | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Authentication \| RADIUS server failed](../alarm-classes-reference/security.md#security-authentication-radius-server-failed) | :material-arrow-up: opening event | dispose |



## Security | Authentication | RADIUS server recovered




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | RADIUS server address | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Authentication \| RADIUS server failed](../alarm-classes-reference/security.md#security-authentication-radius-server-failed) | :material-arrow-down: closing event | dispose |



## Security | Authentication | Rejected
### Symptoms
No specific symptoms


### Probable Causes
User successfully logged out. Session terminated


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |
| server | `ip_address` | Server | {{ no }} |
| user | `str` | User | {{ no }} |
| src_ip | `ip_address` | Outside user ip | {{ no }} |




## Security | Authentication | SNMP Authentication Failure
### Symptoms
NOC, NMS and monitoring systems cannot interact with the box over SNMP protocol


### Probable Causes
SNMP server is misconfigured, community mismatch, misconfigured ACL or brute-force attack in progress


### Recommended Actions
Check SNMP configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Request source address | {{ yes }} |
| community | `str` | Request SNMP community | {{ no }} |




## Security | Authentication | TACACS+ server failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | TACACS+ server address | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Authentication \| TACACS+ server failed](../alarm-classes-reference/security.md#security-authentication-tacacs+-server-failed) | :material-arrow-up: opening event | dispose |



## Security | Authentication | TACACS+ server recovered




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | TACACS+ server address | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Security \| Authentication \| TACACS+ server failed](../alarm-classes-reference/security.md#security-authentication-tacacs+-server-failed) | :material-arrow-down: closing event | dispose |


