# Phone | *


## Phone | SCCP | Register




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Device name | {{ yes }} |
| type | `str` | Device type | {{ yes }} |
| sn | `str` | Device Serial Number | {{ yes }} |
| ip | `ip_address` | Device IP address | {{ yes }} |
| socket | `int` | Socket number | {{ yes }} |




## Phone | SCCP | Register Alarm




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| sn | `str` | Device Serial Number | {{ yes }} |
| socket | `int` | Socket number | {{ no }} |
| image | `str` | Load image | {{ yes }} |
| reason | `str` | Alarm reason | {{ yes }} |




## Phone | SCCP | Register New




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Device name | {{ yes }} |
| type | `str` | Device type | {{ yes }} |
| sn | `str` | Device Serial Number | {{ yes }} |
| ip | `ip_address` | Device IP address | {{ yes }} |
| socket | `int` | Socket number | {{ yes }} |




## Phone | SCCP | Unregister Abnormal




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Device name | {{ yes }} |
| type | `str` | Device type | {{ yes }} |
| sn | `str` | Device Serial Number | {{ yes }} |
| ip | `ip_address` | Device IP address | {{ yes }} |
| socket | `int` | Socket number | {{ yes }} |




## Phone | SCCP | Unregister Normal




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Device name | {{ yes }} |
| type | `str` | Device type | {{ yes }} |
| sn | `str` | Device Serial Number | {{ yes }} |
| ip | `ip_address` | Device IP address | {{ yes }} |
| socket | `int` | Socket number | {{ yes }} |



