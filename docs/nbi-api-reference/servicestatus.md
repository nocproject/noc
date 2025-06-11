# NBI servicestatus API

NBI servicestatus API allows to request current statuses for
specified [Service](../concepts/service/index.md).

## Get Object Status

```
POST /api/nbi/servicestatus
```

Get current statuses for one or more [Service](../concepts/service/index.md).

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    POST /api/nbi/servicestatus HTTP/1.1
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
: Array of [Service](../concepts/service/index.md) ID.

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:servicestatus` API access

### Response Parameters
id (string)
: [Service](../concepts/service/index.md) ID.

status (bool)
: true if object is up, false otherwise.

### HTTP Response Codes

200
: Success

400
: Bad request
