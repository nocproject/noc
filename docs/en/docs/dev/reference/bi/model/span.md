# span model

## Table Structure

| Setting    | Value                                                  |
| ---------- | ------------------------------------------------------ |
| Table Name | span                                                   |
| Engine     | MergeTree(date, (server, service, ts, in_label), 8192) |

| Field      | Data Type | Description     |
| ---------- | --------- | --------------- |
| date       | Date      | Date            |
| ts         | DateTime  | Created         |
| ctx        | UInt64    | Span context    |
| id         | UInt64    | Span id         |
| parent     | UInt64    | Span parent     |
| server     | String    | Called service  |
| service    | String    | Called function |
| client     | String    | Caller service  |
| duration   | UInt64    | Duration (us)   |
| sample     | Int32     | Sampling rate   |
| error_code | UInt32    | Error code      |
| error_text | String    | Error text      |
| in_label   | String    | Input arguments |
| out_label  | String    | Output results  |
