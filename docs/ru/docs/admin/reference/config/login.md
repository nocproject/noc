# [login] section

[Login](../services/login.md) service configuration

## methods

|                |                     |
| -------------- | ------------------- |
| Default value  | `local`             |
| YAML Path      | `login.methods`     |
| Key-Value Path | `login/methods`     |
| Environment    | `NOC_LOGIN_METHODS` |

## session_ttl

|                |                         |
| -------------- | ----------------------- |
| Default value  | `7d`                    |
| YAML Path      | `login.session_ttl`     |
| Key-Value Path | `login/session_ttl`     |
| Environment    | `NOC_LOGIN_SESSION_TTL` |

## language

|                |                      |
| -------------- | -------------------- |
| Default value  | `en`                 |
| YAML Path      | `login.language`     |
| Key-Value Path | `login/language`     |
| Environment    | `NOC_LOGIN_LANGUAGE` |

## restrict_to_group

|                |                               |
| -------------- | ----------------------------- |
| Default value  | ``                            |
| YAML Path      | `login.restrict_to_group`     |
| Key-Value Path | `login/restrict_to_group`     |
| Environment    | `NOC_LOGIN_RESTRICT_TO_GROUP` |

## single_session_group

|                |                                  |
| -------------- | -------------------------------- |
| Default value  | ``                               |
| YAML Path      | `login.single_session_group`     |
| Key-Value Path | `login/single_session_group`     |
| Environment    | `NOC_LOGIN_SINGLE_SESSION_GROUP` |

## mutual_exclusive_group

|                |                                    |
| -------------- | ---------------------------------- |
| Default value  | ``                                 |
| YAML Path      | `login.mutual_exclusive_group`     |
| Key-Value Path | `login/mutual_exclusive_group`     |
| Environment    | `NOC_LOGIN_MUTUAL_EXCLUSIVE_GROUP` |

## idle_timeout

|                |                          |
| -------------- | ------------------------ |
| Default value  | `1w`                     |
| YAML Path      | `login.idle_timeout`     |
| Key-Value Path | `login/idle_timeout`     |
| Environment    | `NOC_LOGIN_IDLE_TIMEOUT` |

## pam_service

|                |                         |
| -------------- | ----------------------- |
| Default value  | `noc`                   |
| YAML Path      | `login.pam_service`     |
| Key-Value Path | `login/pam_service`     |
| Environment    | `NOC_LOGIN_PAM_SERVICE` |

## radius_secret

|                |                           |
| -------------- | ------------------------- |
| Default value  | `noc`                     |
| YAML Path      | `login.radius_secret`     |
| Key-Value Path | `login/radius_secret`     |
| Environment    | `NOC_LOGIN_RADIUS_SECRET` |

## radius_server

|                |                           |
| -------------- | ------------------------- |
| Default value  | ``                        |
| YAML Path      | `login.radius_server`     |
| Key-Value Path | `login/radius_server`     |
| Environment    | `NOC_LOGIN_RADIUS_SERVER` |

## register_last_login

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `True`                          |
| YAML Path      | `login.register_last_login`     |
| Key-Value Path | `login/register_last_login`     |
| Environment    | `NOC_LOGIN_REGISTER_LAST_LOGIN` |

## jwt_cookie_name

|                |                             |
| -------------- | --------------------------- |
| Default value  | `noc_jwt`                   |
| YAML Path      | `login.jwt_cookie_name`     |
| Key-Value Path | `login/jwt_cookie_name`     |
| Environment    | `NOC_LOGIN_JWT_COOKIE_NAME` |

## jwt_algorithm

Default value
: HS256

Possible values
:

- HS256
- HS384
- HS512

YAML Path
: login.jwt_algorithm

Key-Value Path
: login/jwt_algorithm

Environment
: NOC_LOGIN_JWT_ALGORITHM
