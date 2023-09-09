# alarms model

## Table Structure

| Setting    | Value                                       |
| ---------- | ------------------------------------------- |
| Table Name | alarms                                      |
| Engine     | MergeTree(date, (ts, managed_object), 8192) |

| Field                 | Data Type | Description          |
| --------------------- | --------- | -------------------- |
| date                  | Date      | Date                 |
| ts                    | DateTime  | Created              |
| close_ts              | DateTime  | Close Time           |
| duration              | Int32     | Duration             |
| alarm_id              | String    | Id                   |
| root                  | String    | Alarm Root           |
| alarm_class           | UInt64    | Alarm Class          |
| severity              | Int32     | Severity             |
| reopens               | Int32     | Reopens              |
| direct_services       | Int64     | Direct Services      |
| direct_subscribers    | Int64     | Direct Subscribers   |
| total_objects         | Int64     | Total Objects        |
| total_services        | Int64     | Total Services       |
| total_subscribers     | Int64     | Total Subscribers    |
| escalation_ts         | DateTime  | Escalation Time      |
| escalation_tt         | String    | Number of Escalation |
| reboots               | Int16     | Qty of Reboots       |
| managed_object        | UInt64    | Object Name          |
| pool                  | UInt64    | Pool Name            |
| ip                    | UInt32    | IP Address           |
| profile               | UInt64    | Profile              |
| vendor                | UInt64    | Vendor Name          |
| platform              | UInt64    | Platform             |
| version               | UInt64    | Version              |
| administrative_domain | UInt64    | Admin. Domain        |
| segment               | UInt64    | Network Segment      |
| container             | UInt64    | Container            |
| x                     | Float64   | Longitude            |
| y                     | Float64   | Latitude             |
