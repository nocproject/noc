# DataStream Overview

DataStream is an universal REST API intended to stream database actual state
to external systems.

## Streams

DataStream supports multiple `streams` of changes. Each stream
may track actual versions of given type of objects. Each object
reflected in stream only once, though can be reordered in stream
while being changed.

## Change ID

Change ID is 24-character identifier of record's version. Every time
record changed it assigned with new Change ID. Change ID is time-based,
and later changes will lead to greater Change ID.

Following properties of Change ID are viable to understanding DataStream
powers:

- Unique
- Monotonic increase for following changes

## Usage

```
GET /api/datastream/<stream>
```

Get datastream data for a `stream`. Result is a JSON array containing
up to `limit` objects ordered by [Change ID](#change-id).
Each item is an object containing last actualized state.
Empty reply in non-blocking mode (`block` == 0) means that all actualized
changes is already transferred and client may stop and repeat request
after a while.
Connection timeout in blocking mode (`block` == 1) means aborted long polling
due to timeout. Client should retry request immediately.

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    GET /api/datastream/administrativedomain?limit=1 HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345
    ```

<!-- prettier-ignore -->
!!! example "Example Request with Authorization"
    ```
    GET /api/datastream/administrativedomain?limit=1 HTTP/1.1
    Host: noc.example.com
    Authorization: Apikey 12345
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/json
    X-NOC-DataStream-Limit: 1
    X-NOC-DataStream-First-Change: 1
    X-NOC-DataStream-Last-Change: 1
    X-NOC-DataStream-Total: 1

    [
        {
            ...
        }
    ]
    ```

### Query parameters

limit
: Limit amount of records returned per one request. Note
that DataStream service also applies its own configured limits.

block
: Enable/Disable long polling:

- `0`: do not block. Return empty list if no more changes available (default).
- `1`: block until more changes became available.

from
: Return only results with greater [Change ID](#change-id).
Start from beginning if missed.
ISO 8601 timestamp (i.e. YYYY-MM-DDTHH:MM:SS) may be used for time-based references.

filter
: Apply filter function. May be set multiple times.
Filter functions may be global or datastream-specific. Examples:

- `filter=id(123)`
- `filter=pool(default)&filter=shard(0,4)`

### Request Headers

Private-Token or Authorization: Apikey
: [API Key](../concepts/apikey/index.md) with `datastream` API access

### Response Headers

X-NOC-DataStream-Limit
: Actual records limit

X-NOC-DataStream-First-Change
: [Change ID](#change-id) of first change in response (Empty if no changes)

X-NOC-DataStream-Last-Change
: [Change ID](#change-id) of last change in response (Empty if no changes)

X-NOC-DataStream-Total
: Total amount of changes in response

X-NOC-DataStream-More
: Set only if DataStream has more data to query just now

### HTTP Status Codes

200
: Success

403
: Permission Denied

## Authentication

Common [API Key](../concepts/apikey/index.md) scheme is used for client authentication.
[datastream](../concepts/apikey/index.md#datastream-api) API access required.

## Scenarios

### Full Data Fetching

Start from very start and process until stream contains changes

```
change_id = None
while True:
  GET /api/datastream/<поток>?from={change_id}
  change_id = X-NOC-DataStream-Last-Change
  if not change_id:
    break
  for item in response:
      process_item(item)
```

### Incremental Fetching

Last processed [Change ID](#change-id) should
be stored somewhere and restored on next run. This scenario
offers gentle recover in case of `process_item` failure.

```
change_id = restore_change_id()
while True:
  GET /api/datastream/<поток>?from={change_id}
  change_id = X-NOC-DataStream-Last-Change
  if not change_id:
    break
  for item in response:
      process_item(item)
      save_change_id(change_id)
```

### Realtime Streaming

Exploit `block=1` query parameter. Client will block awaiting new
changes. Note that http client may break request during timeout,
so code must catch timeout and repeat request

```
change_id = restore_change_id()
while True:
  GET /api/datastream/<поток>?from={change_id}&block=1
  if timed_out:
      continue
  change_id = X-NOC-DataStream-Last-Change
  for item in response:
      process_item(item)
      save_change_id(change_id)
```

### Record deletion processing

Deleted records remains in stream and marked with `$deleted` key

```
{
  "id": "XXXXX",
  ...
  "$deleted": true
  ...
}
```

## Filters

Default filters set available to all DataStreams

### id(id)

Restrict stream to object with given `id`.

id
: Object id

### shard(instance, n_instances)

Perform stream sharding, splitting stream to `n_instances`
independent parts

instance
: Number of instance `[0 .. n_instances - 1]`

n_instances
: Total amount of instances
