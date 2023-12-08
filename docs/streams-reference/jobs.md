# jobs Stream

`jobs` stream is a part of [Orchestration Pipeline](index.md#orchestration-pipeline).

## Subscribers

- [worker](../services-reference/worker.md) service

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
