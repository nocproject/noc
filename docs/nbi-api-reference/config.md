# NBI config API

NBI config API allows remote system to fetch Managed Object's
configuration, eigther last of specified revision

## Get Last Config
```
GET /api/nbi/config/(int:object_id)
```

Get last configuration for Managed Object with id `object_id`

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    GET /api/nbi/config/333 HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/plain

    !
    hostname Switch
    ...
    ```

### Request Parameters
object_id
: Managed Object's id.

### Request Headers
Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:config` API access.

### HTTP Status Code
200
: Success.

204
: No Content. Config has not been read yet.

404
: Object not found.

## Get Config by Revision
```
GET /api/nbi/config/(int:object_id)/(str:revision id)
```
Get configuration revision `revision_id`
for Managed Object with id `object_id`

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    GET /api/nbi/config/333/5c03cb4cc04567000830be73 HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/plain

    !
    hostname Switch
    ...
    ```

### Request Parameters
object_id
: Managed Object's id

revision
: Config revision. Can be obtained via [configrevisions API](configrevisions.md)

### Request Headers
Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:config` API access

### HTTP Status Codes
200
: Success.

404
: Object not found.
