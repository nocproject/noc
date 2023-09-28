# Phone | *


## Phone | SCCP | Register




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Device name | {{ yes }} |
| type | `str` | Device type | {{ yes }} |
| sn | `str` | Device Serial Number | {{ yes }} |
| ip | `ip_address` | Device IP address | {{ yes }} |
| socket | `int` | Socket number | {{ yes }} |




## Phone | SCCP | Register Alarm




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| sn | `str` | Device Serial Number | {{ yes }} |
| socket | `int` | Socket number | {{ no }} |
| image | `str` | Load image | {{ yes }} |
| reason | `str` | Alarm reason | {{ yes }} |




## Phone | SCCP | Register New




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Device name | {{ yes }} |
| type | `str` | Device type | {{ yes }} |
| sn | `str` | Device Serial Number | {{ yes }} |
| ip | `ip_address` | Device IP address | {{ yes }} |
| socket | `int` | Socket number | {{ yes }} |




## Phone | SCCP | Unregister Abnormal




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Device name | {{ yes }} |
| type | `str` | Device type | {{ yes }} |
| sn | `str` | Device Serial Number | {{ yes }} |
| ip | `ip_address` | Device IP address | {{ yes }} |
| socket | `int` | Socket number | {{ yes }} |




## Phone | SCCP | Unregister Normal




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Device name | {{ yes }} |
| type | `str` | Device type | {{ yes }} |
| sn | `str` | Device Serial Number | {{ yes }} |
| ip | `ip_address` | Device IP address | {{ yes }} |
| socket | `int` | Socket number | {{ yes }} |



