# Discovery


## Discovery | Error | Auth Failed

### Symptoms
Cannot login to managed object


### Probable Causes
Username or password is wrong or ACS Server is unavailable


### Recommended Actions
Check username and password on system and device.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |



## Discovery | Error | Connection Refused

### Symptoms
Connection refused when setup session with managed object


### Probable Causes
Firewall or ACL settings on device or device busy


### Recommended Actions
Check ACL settings on device and it availability


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarm |  |
| message | Error detail message |  |



## Discovery | Error | Low Privileges

### Symptoms
CLI command is not supported in current CLI mode and nothing password for raise permission level


### Probable Causes
Low permission level and not credential to raise it for execute command


### Recommended Actions
Add enable password to managed object settings or grant permission for execute commands


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |



## Discovery | Error | No Super

### Symptoms
Cannot switch to enable mode managed object


### Probable Causes
Password for enable mode is wrong or ACS Server is unavailable


### Recommended Actions
Check username and password on system and device for enable mode


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |



## Discovery | Error | SSH Protocol

### Symptoms
SSH Error when setup session with managed object


### Probable Causes
Unsupported protocol operations when worked with device


### Recommended Actions
Check setup session processed with managed object


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |



## Discovery | Error | Service Not Available

### Symptoms
No getting free activator for run task


### Probable Causes
Activator service down or lost Consul registration


### Recommended Actions
Check activator service and Consul DCS is alive and available check pass


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |



## Discovery | Error | Unhandled Exception

### Symptoms
Exception when worked device on CLI


### Probable Causes
Unsupported protocol operations when worked with devices or other problem


### Recommended Actions
Use script debug tools viewing execute script on device and check traceback on activator host


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message |  |



## Discovery | Guess | CLI Credentials

### Symptoms
When processed logged in devices Username/Password incorrect


### Probable Causes
Username/Password no in local user database on devices or ACS server.


### Recommended Actions
Check managed object settings for rights credentials. Use it for logged in devices. Check device config.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |



## Discovery | Guess | Profile

### Symptoms
Error in response device SA profile


### Probable Causes
Not find profile for OID or HTTP response or wrong SNMP community in device settings


### Recommended Actions
View having prfoile check rules for device


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |



## Discovery | Guess | SNMP Community

### Symptoms
No response SNMP request for community in suggest auth profile.


### Probable Causes
Nothing appropriate SNMP community in suggest profile or no SNMP activate on devices


### Recommended Actions
Check device SNMP configuration and check Suggest authentication profile settings


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| path | Path to alarms |  |
| message | Error detail message  |  |



## Discovery | Job | Box


### Probable Causes
Various errors connecting to the equipment


### Recommended Actions
Connection error - check telnet/ssh port availability on device
Authentication error - check allow access to device with credentials
SNMP error - check SNMP community settings on device



## Discovery | Job | Periodic


### Probable Causes
Various errors connecting to the equipment


### Recommended Actions
Connection error - check telnet/ssh port availability on device
Authentication error - check allow access to device with credentials
SNMP error - check SNMP community settings on device


