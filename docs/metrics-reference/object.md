# Object

Object-related metrics

## Table Structure
The `Object` metric scope is stored
in the `object` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |
| service | sa.Service |



Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="telephony-sip-register-contacts-active"></a>sip_register_contacts_active | UInt64 | Telephony \| SIP \| Register \| Contacts \| Active | The number of SIP Contacts register on local device (not on all cluster, if available). | C | 1 | 1 |
| <a id="telephony-sip-sessions-active"></a>sip_sessions_active | UInt64 | Telephony \| SIP \| Sessions \| Active | The total number of active SIP sessions. | C | 1 | 1 |
| <a id="object-sysuptime"></a>sys_uptime | UInt64 | Object \| SysUptime | Object  RFC1213-MIB:SysUptime  | sec | s | 1 |