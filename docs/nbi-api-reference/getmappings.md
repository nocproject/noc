# NBI getmappings API

NBI `getmappings` API allows remote system to query mappings between
NOC's local identifiers (ID) and the remote system's one.

Consider NOC has got a Managed Object from remote system. Remote
system maintains own ID space, so NOC stores necessary mapping information.
`getmappings` API allows to query object mappings by:

- local ID
- remote system and remote ID

## Request Scopes

Scope is a kind of mappings to request. Possible values:

- `managedobject` - Managed Object mappings

## Query by local id (GET)

```
GET /api/nbi/getmappings?scope=(str:scope)&id=(str:local_id)
```

Get all object's mappings by NOC's ID

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    GET /api/nbi/getmappings?scope=managedobject&id=660 HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 Ok
    Content-Type: text/json
    
    [
      {
        "scope": "managedobject",
        "id": "660",
        "mappings": [
          {
            "remote_system": "5e552150ee23febbffa68ab2",
            "remote_id": "5e552140ee23febbffa68ab1"
          }
        ]
      }
    ]
    ```

### Request Parameters

scope
: Request scope (See [Request Scopes](#request-scopes))

local_id
: NOC's local ID

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:getmappings` API access

### HTTP Status Codes

200
: Success.

400
: Bad request.

404
: Object not found.

500
: Internal error.

## Query by remote id (GET)

```
GET /api/nbi/getmappings?scope=(str:scope)&remote_system=(str:remote_system)&remote_id=(str:remote_id)
```

Get all object's mappings by NOC's ID

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    GET /api/nbi/getmappings?scope=managedobject&remote_system=5e552150ee23febbffa68ab2&remote_id=5e552140ee23febbffa68ab1 HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 Ok
    Content-Type: text/json

    [
      {
        "scope": "managedobject",
        "id": "660",
        "mappings": [
          {
            "remote_system": "5e552150ee23febbffa68ab2",
            "remote_id": "5e552140ee23febbffa68ab1"
          }
        ]
      }
    ]
    ```

### Request Parameters

scope
: Request scope (See [Request Scopes](#request-scopes))

remote_system
: ID of Remote System (NOC settings)

remote_id
: ID from Remote System

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:getmappings` API access

### HTTP Status Codes

200
: Success.

400
: Bad request.

404
: Object not found.

500
: Internal error.

## Query by multiple local and remote ids (GET)

```
GET /api/nbi/getmappings?scope=(str:scope)&remote_system=(str:remote_system)&remote_id=(str:remote_id)
```

Get all object's mappings by NOC's ID

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    GET /api/nbi/getmappings?scope=managedobject&id=10&id=11&remote_system=5e552150ee23febbffa68ab2&remote_id=5e552140ee23febbffa68ab1&&remote_id=5e552140ee23febbffa68ab2 HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 Ok
    Content-Type: text/json

    [
      {
        "scope": "managedobject",
        "id": "10",
        "mappings": [
          {
            "remote_system": "5e552150ee23febbffa68ab2",
            "remote_id": "5e552140ee23febbffa68ab1"
          }
        ]
      },
      {
        "scope": "managedobject",
        "id": "11",
        "mappings": [
          {
            "remote_system": "5e552150ee23febbffa68ab2",
            "remote_id": "5e552140ee23febbffa68ab2"
          }
        ]
      }
    ]
    ```

### Request Parameters

scope
: Request scope (See [Request Scopes](#request-scopes))

remote_system
: ID of Remote System (NOC settings)

remote_id
: ID from Remote System

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:getmappings` API access

### HTTP Status Codes

200
: Success.

400
: Bad Request

404
: Object not found.

500
: Internal error

## Query by local id (POST)

```
POST /api/nbi/getmappings
```

Get all object's mappings by NOC's ID

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    POST /api/nbi/getmappings HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    Content-Type: text/json

    {
      "scope": "managedobject",
      "id": "660"
    }
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 Ok
    Content-Type: text/json

    [
      {
        "scope": "managedobject",
        "id": "660",
        "mappings": [
          {
            "remote_system": "5e552150ee23febbffa68ab2",
            "remote_id": "5e552140ee23febbffa68ab1"
          }
        ]
      }
    ]
    ```

### Request Parameters

scope
: Request scope (See [Request Scopes](#request-scopes))

local_id
: NOC's local ID

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:getmappings` API access

### HTTP Status Codes

200
: Success.

400
: Bad Request

404
: Object not found.

500
: Internal error

## Query by remote id (POST)

```
POST /api/nbi/getmappings
```

Get all object's mappings by NOC's ID

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    POST /api/nbi/getmappings HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    Content-Type: text/json

    {
      "scope": "managedobject",
      "remote_system": "5e552150ee23febbffa68ab2",
      "remote_id": "5e552140ee23febbffa68ab1"
    }
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 Ok
    Content-Type: text/json

    [
      {
        "scope": "managedobject",
        "id": "660",
        "mappings": [
          {
            "remote_system": "5e552150ee23febbffa68ab2",
            "remote_id": "5e552140ee23febbffa68ab1"
          }
        ]
      }
    ]
    ```

scope
: Request scope (See [Request Scopes](#request-scopes))

remote_system
: ID of Remote System (NOC settings)

remote_id
: ID from Remote System

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:getmappings` API access

### HTTP Status Codes

200
: Success.

400
: Bad Request

404
: Object not found.

500
: Internal error

## Query by multiple local and remote ids (POST)

```
POST /api/nbi/getmappings
```

Get all object's mappings by NOC's ID

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    POST /api/nbi/getmappings HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    Content-Type: text/json
    
    {
      "scope": "managedobject",
      "id": ["10", "11"],
      "remote_system": "5e552150ee23febbffa68ab2",
      "remote_id": ["5e552140ee23febbffa68ab1", "5e552140ee23febbffa68ab2"]
    }
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 Ok
    Content-Type: text/json

    [
      {
        "scope": "managedobject",
        "id": "10",
        "mappings": [
          {
            "remote_system": "5e552150ee23febbffa68ab2",
            "remote_id": "5e552140ee23febbffa68ab1"
          }
        ]
      },
      {
        "scope": "managedobject",
        "id": "11",
        "mappings": [
          {
            "remote_system": "5e552150ee23febbffa68ab2",
            "remote_id": "5e552140ee23febbffa68ab2"
          }
        ]
      }
    ]
    ```

### Query Parameters

scope
: Request scope (See [Request Scopes](#request-scopes))

id
: List of local ids

remote_system
: ID of Remote System (NOC settings)

remote_id
: List of IDs from Remote System

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:getmappings` API access

### HTTP Status Codes

200
: Success.

400
: Bad Request

404
: Object not found.

500
: Internal error
