.. _api-nbi-telemetry:

=================
NBI telemetry API
=================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

NBI telemetry API allows remote agents to push collected metrics
to NOC. Refer to :ref:`NBI Objectmetrics API<api-nbi-objectmetrics>`
for details on metrics retrieval.

.. _api-nbi-telemetry-usage:

Usage
-----

.. http:post:: /api/nbi/telemetry

    Push bunch of metrics to NOC.

    **Example Request**:

    .. sourcecode:: http

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

    **Example Response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/json

        "OK"

    :<json string bi_id: :ref:`Managed Object's<reference-managed-object>` BI ID
    :<jsonarr array metrics: List of metrics
    :<json string metric_type: Name of :ref:`Metric Type<metric-types>`
    :<jsonarr array path: Metric Path. Refer to :ref:`Metric Scopes<metrics-scopes>` for details
    :<jsonarr array values: Array of pairs [timestamp, value]. Where timestamp is in ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS)
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:telemetry` API access
    :statuscode 200: Success
