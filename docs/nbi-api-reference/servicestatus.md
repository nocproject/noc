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
 "services": [
     {"id": "671b5838075fb524ae69f930"},
     {"id": "673119a4024bddb8f273e9d2"},
     {"remote_system": "RS1", "remote_id": "427"}
 ]
}
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/json

{
  "statuses": [
    {
      "id": "671b5838075fb524ae69f930",
      "status": {
        "id": 1,
        "name": "UP"
      },
      "change": "2025-02-28T14:16:49",
      "in_maintenance": false,
      "parent": null,
      "remote_mappings": null
    },
    {
      "id": "673119a2024bddb8f273e92e",
      "status": {
        "id": 0,
        "name": "UNKNOWN"
      },
      "change": "2024-11-10T23:37:54.771000",
      "in_maintenance": false,
      "parent": null,
      "remote_mappings": null
    },
    {
      "id": "673119a4024bddb8f273e9d2",
      "status": {
        "id": 1,
        "name": "UP"
      },
      "change": "2024-12-16T13:36:40",
      "in_maintenance": false,
      "parent": null,
      "remote_mappings": null
    }
  ],
  "not_found_queries": null
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
