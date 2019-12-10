.. _api-nbi-objectstatus:

====================
NBI objectstatus API
====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

NBI objectstatus API allows to request current statuses for
specified :ref:`Managed Objects<reference-managed-object>`.

.. _api-nbi-objectstatus-usage:

Usage
-----

.. http:post:: /api/nbi/objectstatus

    Get current statuses for one or more :ref:`Managed Objects<reference-managed-object>`.

    **Example Request**:

    .. sourcecode:: http

        POST /api/nbi/objectstatus HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

        {
            "objects": ["10", "11", "12", "13"]
        }

    **Example Response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/json

        {
            "statuses": [
                {"id": "10", "status": True},
                {"id": "11", "status": True},
                {"id": "12", "status": True},
                {"id": "13", "status": False}
            ]
        }

    :<jsonarr string objects: Array of :ref:`Managed Object's<reference-managed-object>` ID.
    :>jsonarr statuses string id: :ref:`Managed Object's<reference-managed-object>` ID.
    :>jsonarr statuses bool string: true if object is up, false otherwise.
    :statuscode 200: Success
    :statuscode 400: Bad request

