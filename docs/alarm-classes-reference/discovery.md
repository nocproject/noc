# Discovery


## Discovery | Error | Auth Failed

<h3>Symptoms</h3>
Cannot login to managed object


<h3>Probable Causes</h3>
Username or password is wrong or ACS Server is unavailable


<h3>Recommended Actions</h3>
Check username and password on system and device.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |




## Discovery | Error | Connection Refused

<h3>Symptoms</h3>
Connection refused when setup session with managed object


<h3>Probable Causes</h3>
Firewall or ACL settings on device or device busy


<h3>Recommended Actions</h3>
Check ACL settings on device and it availability


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarm |  |
| message | Error detail message |  |




## Discovery | Error | Low Privileges

<h3>Symptoms</h3>
CLI command is not supported in current CLI mode and nothing password for raise permission level


<h3>Probable Causes</h3>
Low permission level and not credential to raise it for execute command


<h3>Recommended Actions</h3>
Add enable password to managed object settings or grant permission for execute commands


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |




## Discovery | Error | No Super

<h3>Symptoms</h3>
Cannot switch to enable mode managed object


<h3>Probable Causes</h3>
Password for enable mode is wrong or ACS Server is unavailable


<h3>Recommended Actions</h3>
Check username and password on system and device for enable mode


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |




## Discovery | Error | SSH Protocol

<h3>Symptoms</h3>
SSH Error when setup session with managed object


<h3>Probable Causes</h3>
Unsupported protocol operations when worked with device


<h3>Recommended Actions</h3>
Check setup session processed with managed object


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |




## Discovery | Error | Service Not Available

<h3>Symptoms</h3>
No getting free activator for run task


<h3>Probable Causes</h3>
Activator service down or lost Consul registration


<h3>Recommended Actions</h3>
Check activator service and Consul DCS is alive and available check pass


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |




## Discovery | Error | Unhandled Exception

<h3>Symptoms</h3>
Exception when worked device on CLI


<h3>Probable Causes</h3>
Unsupported protocol operations when worked with devices or other problem


<h3>Recommended Actions</h3>
Use script debug tools viewing execute script on device and check traceback on activator host


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |




## Discovery | Guess | CLI Credentials

<h3>Symptoms</h3>
When processed logged in devices Username/Password incorrect


<h3>Probable Causes</h3>
Username/Password no in local user database on devices or ACS server.


<h3>Recommended Actions</h3>
Check managed object settings for rights credentials. Use it for logged in devices. Check device config.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |




## Discovery | Guess | Profile

<h3>Symptoms</h3>
Error in response device SA profile


<h3>Probable Causes</h3>
Not find profile for OID or HTTP response or wrong SNMP community in device settings


<h3>Recommended Actions</h3>
View having prfoile check rules for device


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |




## Discovery | Guess | SNMP Community

<h3>Symptoms</h3>
No response SNMP request for community in suggest auth profile.


<h3>Probable Causes</h3>
Nothing appropriate SNMP community in suggest profile or no SNMP activate on devices


<h3>Recommended Actions</h3>
Check device SNMP configuration and check Suggest authentication profile settings


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |




## Discovery | Job | Box


<h3>Probable Causes</h3>
Various errors connecting to the equipment


<h3>Recommended Actions</h3>
Connection error - check telnet/ssh port availability on device
Authentication error - check allow access to device with credentials
SNMP error - check SNMP community settings on device




## Discovery | Job | Periodic


<h3>Probable Causes</h3>
Various errors connecting to the equipment


<h3>Recommended Actions</h3>
Connection error - check telnet/ssh port availability on device
Authentication error - check allow access to device with credentials
SNMP error - check SNMP community settings on device



