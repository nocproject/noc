# NBI objectmetrics API

NBI objectmetrics API allows to request specified metrics
for particular [Managed Objects](../concepts/managed-object/index.md).

## Get Object Metrics

```
POST /api/nbi/objectmetrics
```

Get metrics for one or more [Managed Objects](../concepts/managed-object/index.md).
Maximal allowed time range is limited by
[nbi.objectmetrics_max_interval](../config-reference/nbi.md#objectmetrics_max_interval)
configuration setting.

<!-- prettier-ignore -->
!!! example "Example Request"
    ```
    POST /api/nbi/objectmetrics?limit=1 HTTP/1.1
    Host: noc.example.com
    Private-Token: 12345

    {
        "from": "2018-09-01T00:00:00",
        "to": "2018-09-01T01:00:00",
        "metrics": [
            {
                "object": "660",
                "interfaces": ["Fa0/1", "Fa0/2"],
                "metric_types": ["Interface | Load | In", "Interface | Load | Out"]
            },
            {
                "object": "661",
                "interfaces": ["Gi0/1"],
                "metric_types": ["Interface | Load | In", "Interface | Load | Out"]
            }
        ]
    }
    ```

<!-- prettier-ignore -->
!!! example "Example Response"
    ```
    HTTP/1.1 200 OK
    Content-Type: text/json

    {
        "from": "2018-09-01T00:00:00",
        "to": "2018-09-01T01:00:00",
        "metrics": [
            {
                "object": 660,
                "metric_type": "Interface | Load | In",
                "path": ["", "", "", "Fa0/1"],
                "interface": "Fa0/1",
                "values": [
                    ["2018-09-01T00:00:15", 10],
                    ["2018-09-01T00:05:15", 12],
                    ["2018-09-01T00:10:15", 17],
                    ...
                ]
            },
            ...
        ]
    }
    ```

### Request Parameters
from (string)
: Start of interval timestamp in ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS).

to (string)
: Stop of interval timetamp on ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS).

object (string)
: [Managed Object's](../concepts/managed-object/index.md) ID

interfaces (array of string)
: List of requested interfaces (Only for [Interface Scope](../metrics-reference/index.md)).

metric_types (array of string)
: List of requested [Metric Types](../metrics-reference/index.md) names


### Request Headers

Private-Token
: [API Key](../concepts/apikey/index.md) with `nbi:objectmetrics` API access

### Response Parameters
from (string)
: Start of interval timestamp in ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS).

to (string)
: Stop of interval timetamp on ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS).

object (string)
: [Managed Object's](../concepts/managed-object/index.md) ID

metric_type (string)
: Metric Type name

path (array of strings)
: Metric path

interface (string):
Interface (Only for [Interface Scope](../metrics-reference/index.md)).

values (array of arrays)
: Measured values as pairs of (`timestamp`, `value`)

### HTTP Status Codes
200
: Success