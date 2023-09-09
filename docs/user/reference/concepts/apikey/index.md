# API Key

## Usage

Client **MUST** set `Private-Token` HTTP Request header and set it
with proper _Key_ in order to get access to protected API

Example:

```
curl  -s -D - -k -H 'Private-Token: 12345'  https://noc_url/dev/reference/api/datastream/managedobject`
```

where `12345` is an API token key.

## Roles

### DataStream API

Access to [DataStream API](../../../../dev/reference/api/datastream/index.md)

| API:Role                          | Description                                                                                         |
| --------------------------------- | --------------------------------------------------------------------------------------------------- |
| `datastream:administrativedomain` | [administrativedomain DataStream](../../../../dev/reference/api/datastream/administrativedomain.md) |
| `datastream:alarm`                | [administrativedomain DataStream](../../../../dev/reference/api/datastream/alarm.md)                |
| `datastream:resourcegroup`        | [resourcegroup DataStream](../../../../dev/reference/api/datastream/resourcegroup.md)               |
| `datastream:managedobject`        | [managedobject DataStream](../../../../dev/reference/api/datastream/managedobject.md)               |
| `datastream:dnszone`              | [dnszone DataStream](../../../../dev/reference/api/datastream/dnszone.md) access                    |
| `datastream:cfgmetrics`           | [cfgmetrics DataStream](../../../../dev/reference/api/datastream/cfgmetrics.md) access            |
| `datastream:cfgping`              | [cfgping DataStream](../../../../dev/reference/api/datastream/cfgping.md) access                    |
| `datastream:cfgsyslog`            | [cfgsyslog DataStream](../../../../dev/reference/api/datastream/cfgsyslog.md) access                |
| `datastream:cfgtrap`              | [cfgtrap DataStream](../../../../dev/reference/api/datastream/cfgtrap.md) access                    |
| `datastream:vrf`                  | [vrf DataStream](../../../../dev/reference/api/datastream/vrf.md) access                            |
| `datastream:prefix`               | [prefix DataStream](../../../../dev/reference/api/datastream/prefix.md) access                      |
| `datastream:address`              | [address DataStream](../../../../dev/reference/api/datastream/address.md) access                    |

### NBI API

| API:Role              | Description                                                                            |
| --------------------- | -------------------------------------------------------------------------------------- |
| `nbi:config`          | [NBI config API](../../../../dev/reference/api/nbi/config.md) access                   |
| `nbi:configrevisions` | [NBI configrevisions API](../../../../dev/reference/api/nbi/configrevisions.md) access |
| `nbi:getmappings`     | [NBI getmappings API](../../../../dev/reference/api/nbi/getmappings.md) access         |
| `nbi:objectmetrics`   | [NBI objectmetrics API](../../../../dev/reference/api/nbi/objectmetrics.md) access     |
| `nbi:objectstatus`    | [NBI objectstatus API](../../../../dev/reference/api/nbi/objectstatus.md) access       |
| `nbi:path`            | [NBI path API](../../../../dev/reference/api/nbi/path.md) access                       |
| `nbi:telemetry`       | [NBI telemetry API](../../../../dev/reference/api/nbi/telemetry.md) access             |

## Web interface example

You should fill `Name` and `API key` as required fields.
Also in `API` rows should be `nbi` or `datastream`. In `Role` row should be a role from tables above or `*` (asterisk)

![Edit API](edit_api.png)

You can fill the ACL section or may leave it empty.
Prefix field should be in a IP/net way.

![Edit API ACL](edit_api_acl.png)

Also there is an opportunity to allow requests to API only from whitelist IPs.
You can find this option in Tower, in `nbi`/`datastream` service respectively.

## Best Practices

- Grant separate API Keys for every connected system
- Grant separate API Keys for every developer, Restrict key lifetime
- Grant separate API Keys for every external tester, Restrict key to short lifetime
