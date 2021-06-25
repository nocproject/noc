# jobs Stream

`jobs` stream is a part of [GMX Pipeline](index.md#generic-message-exchange-pipeline).

## Subscribers

- [worker](../../../admin/reference/services/worker.md) service

## Message Headers

`jobs` stream doesn't use any additional headers

## Message Format

```json
[
  {
    "handler": "<path to function>",
    "kwargs": {
      "<arg>": "<value>"
    }
  }, ...
]
```
