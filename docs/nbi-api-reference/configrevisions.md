# NBI configrevisions API

NBI configrevisions API allows remote system to fetch full history
of Managed Object's config revisions.

## Get Config Revisions

```
GET /api/nbi/configrevisions/(int:object_id)
```

Get all config revisions for Managed Object with id `object_id`

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    GET /api/nbi/configrevisions/333 HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/json
    
    [
        {
            "timestamp":"2019-04-23T13:38:59.282000",
            "revision":"5c03cb4cc04567000830be73"
        },
        {
            "timestamp":"2018-05-20T08:09:42.953000",
            "revision":"5c03cb4cc04567000830be77"
        },
        {
            "timestamp":"2016-06-25T08:04:41",
            "revision":"5ca35f6aa2342e1516bf0cd7"
        }
    ]
    ```

## Request Parameters

object_id
: Managed Object's id

## Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:configrevisions` API access

## HTTP Status Codes

200
: Success.

404
: Object not found.
