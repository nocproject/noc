# Config | *


## Config | Config Changed
### Symptoms
Behavior of the network can be changed


### Probable Causes
Device configuration has been changed by user or SA subsystem


### Recommended Actions
No specific action needed unless the change caused unexpected consequences


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |




## Config | Config Copy




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| address | `ip_address` | Server IP | {{ no }} |
| filename | `str` | File name | {{ no }} |
| state | `str` | Copy state | {{ no }} |
| cause | `str` | Copy failed by cause | {{ no }} |




## Config | Config Corrected




### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Config \| Invalid Config](../alarm-classes-reference/config.md#config-invalid-config) | :material-arrow-down: closing event | dispose |



## Config | Config Download Failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Server IP | {{ no }} |
| service | `str` | Service name (ftp, tftp) | {{ no }} |
| user | `str` | User name | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Config \| Config Download Failed](../alarm-classes-reference/config.md#config-config-download-failed) | :material-arrow-up: opening event | dispose |



## Config | Config Downloaded Successfully




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Server IP | {{ no }} |
| service | `str` | Service name (ftp, tftp) | {{ no }} |
| user | `str` | User name | {{ no }} |




## Config | Config Sync Failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| config | `str` | Config type | {{ no }} |




## Config | Config Synced
### Symptoms
No specific symptoms


### Probable Causes
Device configuration been proparated to redundant module


### Recommended Actions
No specific action needed




## Config | Config Upload Failed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Server IP | {{ no }} |
| service | `str` | Service name (ftp, tftp) | {{ no }} |
| user | `str` | User name | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Config \| Config Upload Failed](../alarm-classes-reference/config.md#config-config-upload-failed) | :material-arrow-up: opening event | dispose |



## Config | Config Uploaded Successfully




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Server IP | {{ no }} |
| service | `str` | Service name (ftp, tftp) | {{ no }} |
| user | `str` | User name | {{ no }} |




## Config | Entering Configuration Mode
### Symptoms
Behavior of the network can be changed


### Probable Causes
User switched to configuration mode


### Recommended Actions
No specific action needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |




## Config | Exiting Configuration Mode
### Symptoms
Behavior of the network can be changed


### Probable Causes
User switched off configuration mode


### Recommended Actions
No specific action needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| user | `str` | Username | {{ no }} |




## Config | Invalid Config




### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Config \| Invalid Config](../alarm-classes-reference/config.md#config-invalid-config) | :material-arrow-up: opening event | dispose |


