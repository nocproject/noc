.. _api-nbi-objectmetrics:

=====================
NBI objectmetrics API
=====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

NBI objectmetrics API allows to request specified metrics
for particular :ref:`Managed Objects<reference-managed-object>`.

.. _api-nbi-objectmetrics-usage:

Usage
-----

.. http:post:: /api/nbi/objectmetrics

    Get metrics for one or more :ref:`Managed Objects<reference-managed-object>`.
    Maximal allowed time range is limited by
    :ref:`nbi.objectmetrics_max_interval<config-nbi-objectmetrics_max_interval>`.
    configuration setting.

    **Example Request**:

    .. sourcecode:: http

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

    **Example Response**:

    .. sourcecode:: http

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

    :<json string from: Start of interval timestamp in ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS).
    :<json string to: Stop of interval timetamp on ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS).
    :<jsonarr string object: :ref:`Managed Object's<reference-managed-object>` ID
    :<jsonarr array interfaces: List of requested interfaces (Only for :ref:`Interface Scope<metric-scope-interface>`).
    :<jsonarr array metric_types: List of requested :ref:`Metric Types'<metrics>` names
    :>json string from: Start of interval timestamp in ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS).
    :>json string to: Stop of interval timetamp on ISO 8601 format (i.e. YYYY-MM-DDTHH:MM:SS).
    :>jsonarr string object: :ref:`Managed Object's<reference-managed-object>` ID
    :>jsonarr string metric_type: Metric Type name
    :>jsonarr array path: Metric path
    :>jsonarr string interface: Interface (Only for :ref:`Interface Scope<metric-scope-interface>`).
    :>jsonarr array values: Measured values as pairs of (*timestamp*, *value*)
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:objectmetrics` API access
    :statuscode 200: Success
