# mac model

## Table Structure

| Setting    | Value                                       |
| ---------- | ------------------------------------------- |
| Table Name | mac                                         |
| Engine     | MergeTree(date, (ts, managed_object), 8192) |

| Field             | Data Type | Description       |
| ----------------- | --------- | ----------------- |
| date              | Date      | Date              |
| ts                | DateTime  | Created           |
| managed_object    | UInt64    | Object Name       |
| mac               | UInt64    | MAC               |
| interface         | String    | Interface         |
| interface_profile | UInt64    | Interface Profile |
| segment           | UInt64    | Network Segment   |
| vlan              | UInt16    | VLAN              |
| is_uni            | UInt8     | Is UNI            |
