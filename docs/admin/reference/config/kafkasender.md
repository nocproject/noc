# [kafkasender] section

[Kafkasender](../services/kafkasender.md) service configuration

## bootstrap_servers

|                |                                     |
| -------------- | ----------------------------------- |
| Default value  | ``                                  |
| YAML Path      | `kafkasender.bootstrap_servers`     |
| Key-Value Path | `kafkasender/bootstrap_servers`     |
| Environment    | `NOC_KAFKASENDER_BOOTSTRAP_SERVERS` |

## username

|                |                            |
| -------------- | -------------------------- |
| Default value  | ``                         |
| YAML Path      | `kafkasender.username`     |
| Key-Value Path | `kafkasender/username`     |
| Environment    | `NOC_KAFKASENDER_USERNAME` |

## password

|                |                            |
| -------------- | -------------------------- |
| Default value  | `None`                     |
| YAML Path      | `kafkasender.password`     |
| Key-Value Path | `kafkasender/password`     |
| Environment    | `NOC_KAFKASENDER_PASSWORD` |

## sasl_mechanism

Default value
: PLAIN

Possible values
:

- PLAIN
- GSSAPI
- SCRAM-SHA-256
- SCRAM-SHA-512

YAML Path
: kafkasender.sasl_mechanism

Key-Value Path
: kafkasender/sasl_mechanism

Environment
: NOC_KAFKASENDER_SASL_MECHANISM

## security_protocol

Default value
: PLAINTEXT

Possible values
:

- PLAINTEXT
- SASL_PLAINTEXT
- SSL
- SASL_SSL

YAML Path
: kafkasender.security_protocol

Key-Value Path
: kafkasender/security_protocol

Environment
: NOC_KAFKASENDER_SECURITY_PROTOCOL
