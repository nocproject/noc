# System | *


## System | Halt




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |




## System | Process Crashed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Process name | {{ yes }} |
| pid | `str` | Process PID | {{ no }} |
| status | `str` | Exit status | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [System \| Process Crashed](../alarm-classes-reference/system.md#system-process-crashed) | :material-arrow-up: opening event | dispose |



## System | Process Exited




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Process name | {{ yes }} |
| pid | `str` | Process PID | {{ no }} |
| status | `str` | Exit status | {{ no }} |




## System | Process Started




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Process name | {{ yes }} |
| pid | `str` | Process PID | {{ no }} |




## System | Reboot




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [System \| Reboot](../alarm-classes-reference/system.md#system-reboot) | :material-arrow-up: opening event | dispose |



## System | Started




<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [System \| Reboot](../alarm-classes-reference/system.md#system-reboot) | :material-arrow-down: closing event | dispose |


