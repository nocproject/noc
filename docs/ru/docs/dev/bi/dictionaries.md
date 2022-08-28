# BI Dictionaries


## Administrative Domain

**Name**: `administrative_domain`

| Field  | Data Type | Description           |
| ------ | --------- | --------------------- |
| bi_id  | UInt64    | BI ID                 |
| id     | String    | ID                    |
| name   | String    | None                  |
| parent | UInt64    | `[Hierarchical]` None |


## AlarmClass

**Name**: `alarmclass`

| Field | Data Type | Description |
| ----- | --------- | ----------- |
| bi_id | UInt64    | BI ID       |
| id    | String    | ID          |
| name  | String    | None        |

## Interface Description

**Name**: `interfacedescription`

| Field       | Data Type | Description |
| ----------- | --------- | ----------- |
| bi_id       | UInt64    | BI ID       |
| id          | String    | ID          |
| description | String    | None        |

## Interface Profile

**Name**: `interfaceprofile`

| Field  | Data Type | Description |
| ------ | --------- | ----------- |
| bi_id  | UInt64    | BI ID       |
| id     | String    | ID          |
| name   | String    | None        |
| is_uni | UInt8     | None        |

## Managed Object

**Name**: `managedobject`

| Field    | Data Type | Description |
| -------- | --------- | ----------- |
| bi_id    | UInt64    | BI ID       |
| id       | String    | ID          |
| name     | String    | None        |
| address  | String    | None        |
| profile  | String    | None        |
| platform | String    | None        |
| version  | String    | None        |

## Network Segment

**Name**: `networksegment`

| Field  | Data Type | Description           |
| ------ | --------- | --------------------- |
| bi_id  | UInt64    | BI ID                 |
| id     | String    | ID                    |
| name   | String    | None                  |
| parent | UInt64    | `[Hierarchical]` None |

## Platform

**Name**: `platform`

| Field     | Data Type | Description |
| --------- | --------- | ----------- |
| bi_id     | UInt64    | BI ID       |
| id        | String    | ID          |
| name      | String    | None        |
| vendor    | String    | None        |
| full_name | String    | None        |


## Pool

**Name**: `pool`

| Field | Data Type | Description |
| ----- | --------- | ----------- |
| bi_id | UInt64    | BI ID       |
| id    | String    | ID          |
| name  | String    | None        |

## Vendor

**Name**: `vendor`

| Field | Data Type | Description |
| ----- | --------- | ----------- |
| bi_id | UInt64    | BI ID       |
| id    | String    | ID          |
| name  | String    | None        |


## Version

**Name**: `version`

| Field   | Data Type | Description |
| ------- | --------- | ----------- |
| bi_id   | UInt64    | BI ID       |
| id      | String    | ID          |
| name    | String    | None        |
| profile | String    | None        |
| vendor  | String    | None        |
