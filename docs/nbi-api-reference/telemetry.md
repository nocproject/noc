# NBI telemetry API

NBI telemetry API allows remote agents to push collected metrics
to NOC. Refer to [NBI Objectmetrics API](objectmetrics.md)
for details on metrics retrieval.

## Send Telemetry

```
POST /api/nbi/telemetry
```

Push bunch of metrics to NOC.

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    POST /api/nbi/telemetry HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345

    {
        "bi_id": "123456",
        "metrics": [
            {
                "metric_type": "Interface | Load | In",
                "path": ["", "", "", "Fa0/1"],
                "values": [
                    ["2019-04-08T13:50:00", 12000],
                    ["2019-04-08T13:55:00", 12200],
                    ["2019-04-08T14:00:00", 50000]
                ]
            },
            {
                "metric_type": "Interface | Load | Out",
                "path": ["", "", "", "Fa0/1"],
                "values": [
                    ["2019-04-08T13:50:00", 500000],
                    ["2019-04-08T13:55:00", 520000],
                    ["2019-04-08T14:00:00", 540000]
                ]
            },
        ]
    }
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/json

    "OK"
    ```

### Request Parameters
bi_id (string)
: [Managed Object's](../concepts/managed-object/index.md)` BI ID

metrics (array of objects)
: List of metrics

metric_type (string)
: Name of [Metric Type](../metrics-reference/index.md)

path (array of string)
: Metric Path. Refer to [Metric Scopes](../metrics-reference/index.md) for details

values (array of array)
: Array of pairs (`timestamp`, `value`). Where timestamp is in ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS)

### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:telemetry` API access

### HTTP Status Codes

200
: Success
