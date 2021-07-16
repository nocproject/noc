# [pg] section

Pg service configuration

## addresses

|                |                                                               |
| -------------- | ------------------------------------------------------------- |
| Default value  | `service="postgres", wait=True, near=True, full_result=False` |
| YAML Path      | `pg.addresses`                                                |
| Key-Value Path | `pg/addresses`                                                |
| Environment    | `NOC_PG_ADDRESSES`                                            |

## db

|                |             |
| -------------- | ----------- |
| Default value  | `noc`       |
| YAML Path      | `pg.db`     |
| Key-Value Path | `pg/db`     |
| Environment    | `NOC_PG_DB` |

## user

|                |               |
| -------------- | ------------- |
| Default value  | ``            |
| YAML Path      | `pg.user`     |
| Key-Value Path | `pg/user`     |
| Environment    | `NOC_PG_USER` |

## password

|                |                   |
| -------------- | ----------------- |
| Default value  | `None`            |
| YAML Path      | `pg.password`     |
| Key-Value Path | `pg/password`     |
| Environment    | `NOC_PG_PASSWORD` |

## connect_timeout

|                |                          |
| -------------- | ------------------------ |
| Default value  | `5`                      |
| YAML Path      | `pg.connect_timeout`     |
| Key-Value Path | `pg/connect_timeout`     |
| Environment    | `NOC_PG_CONNECT_TIMEOUT` |
