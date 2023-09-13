# NBI path API

NBI path API allows to trace possible paths in discovered network
topology considering extra constraints.

## Usage

```
POST /api/nbi/path
```

Trace k-shortest paths over network topology considering constraints.

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    POST /api/nbi/path  HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345

    {
        "from": <path start specification>,
        "to": <path end specification>,
        "config": <path config specification>,
        "constraints": <path constraint specification>
    }
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/json

    {
        "status": true,
        "time": 0.012,
        "paths": [
            {
                "path": [
                    {
                        "links": [
                            {
                                "objects": [
                                    {
                                        "interfaces": [
                                            "Eth 1/27"
                                        ],
                                        "object": {
                                            "address": "172.11.101.209",
                                            "bi_id": 1362320908973547200,
                                            "id": 40046,
                                            "name": "sw1"
                                        }
                                    },
                                    {
                                        "interfaces": [
                                            "Eth 1/52"
                                        ],
                                        "object": {
                                            "address": "172.11.103.20",
                                            "bi_id": 6072199926162248000,
                                            "id": 17918,
                                            "name": "sw2"
                                        }
                                    }
                                ]
                            },
                            ...
                        ]
                    },
                    ...
                ],
                "cost": {
                    "l2": 6
                }
            },
            ...
        ]
    }
    ```

### Request Parameters

from (object)
: Start of path reference (See [Path Start Specification](#path-start-specification))

to (object)
: End of path reference (See [Path End Specification](#path-end-specification))

config (object)
: Configuration (See [Path Config Specification](#path-config-specification))

constraints (object)
: Path Constraints (See [Path Constraints Specification](#path-constraints-specification))

### Request Headers
Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:path` API access

### Response Parameters

status (bool)
: Request status, `true` if success

error (string)
: Error text, only if `status` is `false`.

time (float)
: Request processing time in seconds.

paths (array of objects)
: Paths found, only if `status` is `true`.

### HTTP Status Codes

200
: Success

## Path Start Specification

Path Start specified as value of `from` request key and can be
either Managed Object, interface or service reference.

### Managed Object By Id

```
{
    "object": {
        "id": 12345
    }
}
```

Where `12345` is the [Managed Object](../concepts/managed-object/index.md) Id

### Managed Object By Id and Interface Name

```
{
    "object": {
        "id": 12345
    },
    "interface": {
        "name": "Gi 0/1"
    }
}
```

Where `12345` is the [Managed Object](../concepts/managed-object/index.md) Id and `Gi O/1`
is the normalized interface name.

### Managed Object By Remote Id

```
{
    "object": {
        "remote_system": "6789",
        "remote_id": "1011"
    }
}
```

Where `6789` is the [Remote System](../concepts/remote-system/index.md) Id and
`1011` is the [Managed Object](../concepts/managed-object/index.md) Id in Remote System.

### Managed Object By Remote Id and Interface

```
{
    "object": {
        "remote_system": "6789",
        "remote_id": "1011"
    },
    "interface": {
        "name": "Gi 0/1"
    }
}
```

Where `6789` is the [Remote System](../concepts/remote-system/index.md) Id,
`1011` is the [Managed Object](../concepts/managed-object/index.md) Id in Remote System
and `Gi O/1` is the normalized interface name.

### Interface by Id

```
{
    "interface": {
        "id": "1234567"
    }
}
```

Where `1234567` is the Interface Id

### Service by Id

```
{
    "service": {
        "id": 12345
    }
}
```

Where `12345` is the [Service](../concepts/service/index.md) Id

### Service by Remote Id

```
{
    "service": {
        "remote_system": "6789",
        "remote_id": "1011"
    }
}
```

Where `6789` is the [Service](../concepts/service/index.md) Id and
`1011` is the [Service](../concepts/service/index.md) Id in Remote System.

### Service by Order Id

```
{
    "service": {
        "order_id": "1234"
    }
}
```

Where `1234` is Order Fulfilment order id.
Or:

```
{
    "service": {
        "order_id": "1234",
        "remote_system": "5678"
    }
}
```

The same, but restricted to remote system id `5678`



## Path End Specification

Path End specified as value of `to` request key.

* Explicit specification

  * Managed Object
  * Interface
  * Service

* Implicit specification

  * Object level


### Managed Object By Id

```
{
    "object": {
        "id": 12345
    }
}
```

Where `12345` is the [Managed Object](../concepts/managed-object/index.md) Id

### Managed Object By Id and Interface Name

```
{
    "object": {
        "id": 12345
    },
    "interface": {
        "name": "Gi 0/1"
    }
}
```

Where `12345` is the [Managed Object](../concepts/managed-object/index.md) Id and `Gi O/1`
is the normalized interface name.

### Managed Object By Remote Id

```
{
    "object": {
        "remote_system": "6789",
        "remote_id": "1011"
    }
}
```

Where `6789` is the [Remote Service](../concepts/remote-system/index.md) Id and
`1011` is the [Managed Object](../concepts/managed-object/index.md) Id in Remote System.

### Managed Object By Remote Id and Interface

```
{
    "object": {
        "remote_system": "6789",
        "remote_id": "1011"
    },
    "interface": {
        "name": "Gi 0/1"
    }
}
```

Where `6789` is the [Remote System](../concepts/remote-system/index.md) Id,
`1011` is the [Managed Object](../concepts/managed-object/index.md) Id in Remote System
and `Gi O/1` is the normalized interface name.

### Interface by Id

```
{
    "interface": {
        "id": "1234567"
    }
}
```

Where `1234567` is the Interface Id

### Service by Id

```
{
    "service": {
        "id": 12345
    }
}
```

Where `12345` is the [Service](../concepts/service/index.md) Id

### Service by Remote Id

```
{
    "service": {
        "remote_system": "6789",
        "remote_id": "1011"
    }
}
```

Where `6789` is the [Service](../concepts/service/index.md) Id and
`1011` is the [Service](../concepts/service/index.md) Id in Remote System.

### By Object Level

```
{
    "level": 30
}
```

Specify path end by reaching Managed Object [Level](../concepts/managed-object-profile/index.md#level)
greater than specified.

## Path Config Specification

Path Config specified as value of `config` request key.

```
{
    "max_depth": 10,
    "n_shortest": 2
}
```

Where:

* `max_depth` - Restrict search depth up to `max_depth` nodes.
* `n_shortest` - Return up to `n_shortest` paths.



## Path Constraints Specification

Path Constraints are specified as value of `constraints` request key.

### Explicit VLAN

```
{
    "vlan": {
        "vlan": 1234,
        "strict": false
    }
}
```

Restrict paths to links having VLAN `1234`, either tagged or untagged.
`strict` parameter enforces additional checking:

* `true` - VLAN must be present on both sides of the link.
* `false` - VLAN must be present at least on one side of the link.

### Implicit VLAN

```
{
    "vlan": {
        "interface_untagged": true,
        "strict": true
    }
}
```

Get untagged vlan from start of path interface and restrict path
to links having this VLAN, either tagged or untagged.

`strict` parameter enforces additional checking:

* `true` - VLAN must be present on both sides of the link.
* `false` - VLAN must be present at least on one side of the link.

### Upward Direction

```
{
    "upwards": true
}
```

Forces upward direction of path.
i.e. Managed Object [Level](../concepts/managed-object-profile/index.md#level)
of each next object of the path may not be less that level of current
object. Effectively speed-ups path finding by denying descending to
lower levels of networks.
