# [nsqlookupd] section

Nsqlookupd service configuration

## addresses

|                |                                                                 |
| -------------- | --------------------------------------------------------------- |
| Default value  | `service="nsqlookupd", wait=True, near=True, full_result=False` |
| YAML Path      | `nsqlookupd.addresses`                                          |
| Key-Value Path | `nsqlookupd/addresses`                                          |
| Environment    | `NOC_NSQLOOKUPD_ADDRESSES`                                      |

## http_addresses

|                |                                                          |
| -------------- | -------------------------------------------------------- |
| Default value  | `service="nsqlookupdhttp", wait=True, full_result=False` |
| YAML Path      | `nsqlookupd.http_addresses`                              |
| Key-Value Path | `nsqlookupd/http_addresses`                              |
| Environment    | `NOC_NSQLOOKUPD_HTTP_ADDRESSES`                          |
