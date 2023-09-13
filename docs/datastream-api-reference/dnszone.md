# dnszone DataStream

`dnszone` [DataStream](index.md) contains summarized [DNS Zone](../concepts/dns-zone/index.md)
state, including zone's serial and Resource Records.

## Fields

| Name               | Type                          | Description                                   |
| ------------------ | ----------------------------- | --------------------------------------------- |
| id                 | String                        | [DNS Zone](../concepts/dns-zone/index.md) ID  |
| name               | String                        | Zone Name (Domain name)                       |
| serial             | String                        | Zone's serial                                 |
| masters            | Array of String               | List of master nameservers                    |
| slaves             | Array of String               | List of slave nameservers                     |
| records            | Array of Object {{ complex }} | List of zone's resource records               |
| {{ tab }} name     | String                        | Record name                                   |
| {{ tab }} type     | String                        | Record type (i.e. A, NS, CNAME, ...)          |
| {{ tab }} rdata    | String                        | Record value                                  |
| {{ tab }} ttl      | Integer                       | (Optional) Record's time-to-live              |
| {{ tab }} priority | Integer                       | (Optional) Record's priority (for MX and SRV) |

## Filters

### server(name)

Restrict stream to zones belonging to server `name`

name
: Server name (i.e. `ns1.example.com`)

## Access

[API Key](../concepts/apikey/index.md) with `datastream:dnszone` permissions
required.
