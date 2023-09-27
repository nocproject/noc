# System | *


## System | Halt




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |




## System | Process Crashed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Process name | {{ yes }} |
| pid | `str` | Process PID | {{ no }} |
| status | `str` | Exit status | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [System \| Process Crashed](../alarm-classes-reference/system.md#system-process-crashed) | :material-arrow-up: opening event | dispose |



## System | Process Exited




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Process name | {{ yes }} |
| pid | `str` | Process PID | {{ no }} |
| status | `str` | Exit status | {{ no }} |




## System | Process Started




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Process name | {{ yes }} |
| pid | `str` | Process PID | {{ no }} |




## System | Reboot




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [System \| Reboot](../alarm-classes-reference/system.md#system-reboot) | :material-arrow-up: opening event | dispose |



## System | Started




### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [System \| Reboot](../alarm-classes-reference/system.md#system-reboot) | :material-arrow-down: closing event | dispose |


