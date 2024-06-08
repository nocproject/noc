# Config | *


## Config | Config Changed
<h3>Symptoms</h3>
Behavior of the network can be changed


<h3>Probable Causes</h3>
Device configuration has been changed by user or SA subsystem


<h3>Recommended Actions</h3>
No specific action needed unless the change caused unexpected consequences


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |




## Config | Config Copy




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| address | `ip_address` | Server IP | {{ no }} |
| filename | `str` | File name | {{ no }} |
| state | `str` | Copy state | {{ no }} |
| cause | `str` | Copy failed by cause | {{ no }} |




## Config | Config Corrected




<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Config \| Invalid Config](../alarm-classes-reference/config.md#config-invalid-config) | :material-arrow-down: closing event | dispose |



## Config | Config Download Failed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Server IP | {{ no }} |
| service | `str` | Service name (ftp, tftp) | {{ no }} |
| user | `str` | User name | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Config \| Config Download Failed](../alarm-classes-reference/config.md#config-config-download-failed) | :material-arrow-up: opening event | dispose |



## Config | Config Downloaded Successfully




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Server IP | {{ no }} |
| service | `str` | Service name (ftp, tftp) | {{ no }} |
| user | `str` | User name | {{ no }} |




## Config | Config Sync Failed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| config | `str` | Config type | {{ no }} |




## Config | Config Synced
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
Device configuration been proparated to redundant module


<h3>Recommended Actions</h3>
No specific action needed




## Config | Config Upload Failed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Server IP | {{ no }} |
| service | `str` | Service name (ftp, tftp) | {{ no }} |
| user | `str` | User name | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Config \| Config Upload Failed](../alarm-classes-reference/config.md#config-config-upload-failed) | :material-arrow-up: opening event | dispose |



## Config | Config Uploaded Successfully




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Server IP | {{ no }} |
| service | `str` | Service name (ftp, tftp) | {{ no }} |
| user | `str` | User name | {{ no }} |




## Config | Entering Configuration Mode
<h3>Symptoms</h3>
Behavior of the network can be changed


<h3>Probable Causes</h3>
User switched to configuration mode


<h3>Recommended Actions</h3>
No specific action needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |




## Config | Exiting Configuration Mode
<h3>Symptoms</h3>
Behavior of the network can be changed


<h3>Probable Causes</h3>
User switched off configuration mode


<h3>Recommended Actions</h3>
No specific action needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |




## Config | Invalid Config




<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Config \| Invalid Config](../alarm-classes-reference/config.md#config-invalid-config) | :material-arrow-up: opening event | dispose |


