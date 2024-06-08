# NBI objectstatus API

NBI objectstatus API allows to request current statuses for
specified [Managed Objects](../concepts/managed-object/index.md).

## Get Object Status

```
POST /api/nbi/objectstatus
```

Get current statuses for one or more [Managed Objects](../concepts/managed-object/index.md).

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    POST /api/nbi/objectstatus HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345

    {
        "objects": ["10", "11", "12", "13"]
    }
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/json

    {
        "statuses": [
            {"id": "10", "status": True},
            {"id": "11", "status": True},
            {"id": "12", "status": True},
            {"id": "13", "status": False}
        ]
    }
    ```

### Request Parameters
objects
: Array of [Managed Objects'](../concepts/managed-object/index.md) ID.

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:objectstatus` API access

### Response Parameters
id (string)
: [Managed Objects](../concepts/managed-object/index.md) ID.

status (bool)
: true if object is up, false otherwise.

### HTTP Response Codes

200
: Success

400
: Bad request
