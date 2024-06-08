# Unknown | *


## Unknown | Default
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
No matching classification rule found


<h3>Recommended Actions</h3>
Grab this event, create appropriative classification rule and reclassify the event again




## Unknown | Ignore
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
Event without any usable information for FM


<h3>Recommended Actions</h3>
No specific action needed




## Unknown | SNMP Trap
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
No matching classification rule found


<h3>Recommended Actions</h3>
Grab this event, create appropriative classification rule and reclassify the event again


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| trap_oid | `oid` | SNMP Trap OID | {{ yes }} |
| trap_name | `str` | SNMP Trap name | {{ no }} |




## Unknown | Syslog
<h3>Symptoms</h3>
No specific symptoms


<h3>Probable Causes</h3>
No matching classification rule found


<h3>Recommended Actions</h3>
Grab this event, create appropriative classification rule and reclassify the event again


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| syslog_message | `str` | Full syslog message | {{ yes }} |



