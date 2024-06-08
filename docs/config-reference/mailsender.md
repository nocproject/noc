# [mailsender] section

[Mailsender](../services-reference/mailsender.md) service configuration

## smtp_server

|                |                              |
| -------------- | ---------------------------- |
| Default value  | ``                           |
| YAML Path      | `mailsender.smtp_server`     |
| Key-Value Path | `mailsender/smtp_server`     |
| Environment    | `NOC_MAILSENDER_SMTP_SERVER` |

## smtp_port

|                |                            |
| -------------- | -------------------------- |
| Default value  | `25`                       |
| YAML Path      | `mailsender.smtp_port`     |
| Key-Value Path | `mailsender/smtp_port`     |
| Environment    | `NOC_MAILSENDER_SMTP_PORT` |

## use_tls

|                |                          |
| -------------- | ------------------------ |
| Default value  | `False`                  |
| YAML Path      | `mailsender.use_tls`     |
| Key-Value Path | `mailsender/use_tls`     |
| Environment    | `NOC_MAILSENDER_USE_TLS` |

## helo_hostname

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `noc`                          |
| YAML Path      | `mailsender.helo_hostname`     |
| Key-Value Path | `mailsender/helo_hostname`     |
| Environment    | `NOC_MAILSENDER_HELO_HOSTNAME` |

## from_address

|                |                               |
| -------------- | ----------------------------- |
| Default value  | `noc@example.com`             |
| YAML Path      | `mailsender.from_address`     |
| Key-Value Path | `mailsender/from_address`     |
| Environment    | `NOC_MAILSENDER_FROM_ADDRESS` |

## smtp_user

|                |                            |
| -------------- | -------------------------- |
| Default value  | ``                         |
| YAML Path      | `mailsender.smtp_user`     |
| Key-Value Path | `mailsender/smtp_user`     |
| Environment    | `NOC_MAILSENDER_SMTP_USER` |

## smtp_password

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `None`                         |
| YAML Path      | `mailsender.smtp_password`     |
| Key-Value Path | `mailsender/smtp_password`     |
| Environment    | `NOC_MAILSENDER_SMTP_PASSWORD` |
