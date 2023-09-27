# Unknown | *


## Unknown | Default
### Symptoms
No specific symptoms


### Probable Causes
No matching classification rule found


### Recommended Actions
Grab this event, create appropriative classification rule and reclassify the event again




## Unknown | Ignore
### Symptoms
No specific symptoms


### Probable Causes
Event without any usable information for FM


### Recommended Actions
No specific action needed




## Unknown | SNMP Trap
### Symptoms
No specific symptoms


### Probable Causes
No matching classification rule found


### Recommended Actions
Grab this event, create appropriative classification rule and reclassify the event again


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| trap_oid | `oid` | SNMP Trap OID | {{ yes }} |
| trap_name | `str` | SNMP Trap name | {{ no }} |




## Unknown | Syslog
### Symptoms
No specific symptoms


### Probable Causes
No matching classification rule found


### Recommended Actions
Grab this event, create appropriative classification rule and reclassify the event again


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| syslog_message | `str` | Full syslog message | {{ yes }} |



