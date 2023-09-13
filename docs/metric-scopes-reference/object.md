---
uuid: 76d4d6de-a981-4d30-820c-466cd80d792a
---
# Object Metric Scope

Object-related metrics

## Data Table

ClickHouse Table: `object`

| Field                                                                                               | Type     | Description                                                                                                               |
| --------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------- |
| date                                                                                                | Date     | Measurement Date                                                                                                          |
| ts                                                                                                  | DateTime | Measurement Timestamp                                                                                                     |
| [sip_register_contacts_active](../metric-types-reference/telephony/sip/register/contacts/active.md) | UInt64   | [Telephony \| SIP \| Register \| Contacts \| Active](../metric-types-reference/telephony/sip/register/contacts/active.md) |
| [sip_sessions_active](../metric-types-reference/telephony/sip/sessions/active.md)                   | UInt64   | [Telephony \| SIP \| Sessions \| Active](../metric-types-reference/telephony/sip/sessions/active.md)                      |
| [sys_uptime](../metric-types-reference/object/sysuptime.md)                                         | UInt64   | [Object \| SysUptime](../metric-types-reference/object/sysuptime.md)                                                      |
