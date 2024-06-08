# events model

## Table Structure

| Setting    | Value                                       |
| ---------- | ------------------------------------------- |
| Table Name | alarms                                      |
| Engine     | MergeTree(date, (date, managed_object, event_class), 8192) |

| Field                 | Data Type | Description          |
| --------------------- | --------- | -------------------- |
| date                  | Date      | Date                 |
| ts                    | DateTime  | Created              |
| start_ts              | DateTime  | Close Time           |
| event_id              | String    | Id                   |
| event_class           | UInt64    | Event Class          |
| source                | String    | Event Source         |
| repeat_hash           | String    | Event Repeat Hash    |
| raw_vars              | String    | Event Raw Vars       |
| resolved_vars         | String    | Event Resolved Vars  |
| vars                  | String    | Event Vars           |
| snmp_trap_oid         | String    | SNMP Trap OID        |
| message               | String    | Syslog Message       |
| managed_object        | UInt64    | Object Name          |
| pool                  | UInt64    | Pool Name            |
| ip                    | UInt32    | IP Address           |
| profile               | UInt64    | Profile              |
| vendor                | UInt64    | Vendor Name          |
| platform              | UInt64    | Platform             |
| version               | UInt64    | Version              |
| administrative_domain | UInt64    | Admin. Domain        |
