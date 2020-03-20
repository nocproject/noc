.. _api-nbi-getmappings:

===================
NBI getmappings API
===================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 2
    :class: singlecol

NBI `getmappings` API allows remote system to query mappings between
NOC's local identifiers (ID) and the remote system's one.

Consider NOC has got a Managed Object from remote system. Remote
system maintains own ID space, so NOC stores necessary mapping information.
`getmappings` API  allows to query object mappings by:

* local ID
* remote system and remote ID

.. _api-nbi-getmappings-scopes:

Request Scopes
--------------
Scope is a kind of mappings to request. Possible values:

* `managedobject` - Managed Object mappings

.. _api-nbi-getmappings-usage:

Usage
-----

.. _api-nbi-getmappings-usage-get-local:

Query by local id (GET)
^^^^^^^^^^^^^^^^^^^^^^^

.. http:get:: /api/nbi/getmappings?scope=(str:scope)&id=(str:local_id)

    Get all object's mappings by NOC's ID

    **Example Request**

    .. sourcecode:: http

        GET /api/nbi/getmappings?scope=managedobject&id=660 HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

      **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 Ok
        Content-Type: text/json

        [
          {
            "scope": "managedobject",
            "id": "660",
            "mappings": [
              {
                "remote_system": "5e552150ee23febbffa68ab2",
                "remote_id": "5e552140ee23febbffa68ab1"
              }
            ]
          }
        ]

    :param scope: Request scope (See :ref:`Request Scopes<api-nbi-getmappings-scopes>`)
    :param local_id:  NOC's local ID
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:getmappings` API access.
    :statuscode 200: Success.
    :statuscode 400: Bad request.
    :statuscode 404: Object not found.
    :statuscode 500: Internal error.

.. _api-nbi-getmappings-usage-get-remote:

Query by remote id (GET)
^^^^^^^^^^^^^^^^^^^^^^^^

.. http:get:: /api/nbi/getmappings?scope=(str:scope)&remote_system=(str:remote_system)&remote_id=(str:remote_id)

    Get all object's mappings by NOC's ID

    **Example Request**

    .. sourcecode:: http

        GET /api/nbi/getmappings?scope=managedobject&remote_system=5e552150ee23febbffa68ab2&remote_id=5e552140ee23febbffa68ab1 HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

      **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 Ok
        Content-Type: text/json

        [
          {
            "scope": "managedobject",
            "id": "660",
            "mappings": [
              {
                "remote_system": "5e552150ee23febbffa68ab2",
                "remote_id": "5e552140ee23febbffa68ab1"
              }
            ]
          }
        ]

    :param scope: Request scope (See :ref:`Request Scopes<api-nbi-getmappings-scopes>`)
    :param remote_system: ID of Remote System (NOC settings)
    :param remote_id: ID from Remote System
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:getmappings` API access.
    :statuscode 200: Success.
    :statuscode 400: Bad request.
    :statuscode 404: Object not found.
    :statuscode 500: Internal error.

.. _api-nbi-getmappings-usage-multi-get:

Query by multiple local and remote ids (GET)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. http:get:: /api/nbi/getmappings?scope=(str:scope)&remote_system=(str:remote_system)&remote_id=(str:remote_id)

    Get all object's mappings by NOC's ID

    **Example Request**

    .. sourcecode:: http

        GET /api/nbi/getmappings?scope=managedobject&id=10&id=11&remote_system=5e552150ee23febbffa68ab2&remote_id=5e552140ee23febbffa68ab1&&remote_id=5e552140ee23febbffa68ab2 HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

      **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 Ok
        Content-Type: text/json

        [
          {
            "scope": "managedobject",
            "id": "10",
            "mappings": [
              {
                "remote_system": "5e552150ee23febbffa68ab2",
                "remote_id": "5e552140ee23febbffa68ab1"
              }
            ]
          },
          {
            "scope": "managedobject",
            "id": "11",
            "mappings": [
              {
                "remote_system": "5e552150ee23febbffa68ab2",
                "remote_id": "5e552140ee23febbffa68ab2"
              }
            ]
          }
        ]

    :param scope: Request scope (See :ref:`Request Scopes<api-nbi-getmappings-scopes>`)
    :param remote_system: ID of Remote System (NOC settings)
    :param remote_id: ID from Remote System
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:getmappings` API access.
    :statuscode 200: Success.
    :statuscode 400: Bad request.
    :statuscode 404: Object not found.
    :statuscode 500: Internal error.

.. _api-nbi-getmappings-usage-post-local:

Query by local id (POST)
^^^^^^^^^^^^^^^^^^^^^^^^

.. http:post:: /api/nbi/getmappings

    Get all object's mappings by NOC's ID

    **Example Request**

    .. sourcecode:: http

        POST /api/nbi/getmappings HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345
        Content-Type: text/json

        {
          "scope": "managedobject",
          "id": "660"
        }

      **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 Ok
        Content-Type: text/json

        [
          {
            "scope": "managedobject",
            "id": "660",
            "mappings": [
              {
                "remote_system": "5e552150ee23febbffa68ab2",
                "remote_id": "5e552140ee23febbffa68ab1"
              }
            ]
          }
        ]

    :param scope: Request scope (See :ref:`Request Scopes<api-nbi-getmappings-scopes>`)
    :param local_id:  NOC's local ID
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:getmappings` API access.
    :statuscode 200: Success.
    :statuscode 400: Bad request.
    :statuscode 404: Object not found.
    :statuscode 500: Internal error.

.. _api-nbi-getmappings-usage-post-remote:

Query by remote id (POST)
^^^^^^^^^^^^^^^^^^^^^^^^^
.. http:post:: /api/nbi/getmappings

    Get all object's mappings by NOC's ID

    **Example Request**

    .. sourcecode:: http

        POST /api/nbi/getmappings HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345
        Content-Type: text/json

        {
          "scope": "managedobject",
          "remote_system": "5e552150ee23febbffa68ab2",
          "remote_id": "5e552140ee23febbffa68ab1"
        }

      **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 Ok
        Content-Type: text/json

        [
          {
            "scope": "managedobject",
            "id": "660",
            "mappings": [
              {
                "remote_system": "5e552150ee23febbffa68ab2",
                "remote_id": "5e552140ee23febbffa68ab1"
              }
            ]
          }
        ]

    :param scope: Request scope (See :ref:`Request Scopes<api-nbi-getmappings-scopes>`)
    :param remote_system: ID of Remote System (NOC settings)
    :param remote_id: ID from Remote System
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:getmappings` API access.
    :statuscode 200: Success.
    :statuscode 400: Bad request.
    :statuscode 404: Object not found.
    :statuscode 500: Internal error.

.. _api-nbi-getmappings-usage-post-remote:

Query by multiple local and remote ids (POST)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. http:post:: /api/nbi/getmappings

    Get all object's mappings by NOC's ID

    **Example Request**

    .. sourcecode:: http

        POST /api/nbi/getmappings HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345
        Content-Type: text/json

        {
          "scope": "managedobject",
          "id": ["10", "11"],
          "remote_system": "5e552150ee23febbffa68ab2",
          "remote_id": ["5e552140ee23febbffa68ab1", "5e552140ee23febbffa68ab2"]
        }

      **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 Ok
        Content-Type: text/json

        [
          {
            "scope": "managedobject",
            "id": "10",
            "mappings": [
              {
                "remote_system": "5e552150ee23febbffa68ab2",
                "remote_id": "5e552140ee23febbffa68ab1"
              }
            ]
          },
          {
            "scope": "managedobject",
            "id": "11",
            "mappings": [
              {
                "remote_system": "5e552150ee23febbffa68ab2",
                "remote_id": "5e552140ee23febbffa68ab2"
              }
            ]
          }
        ]
    :param scope: Request scope (See :ref:`Request Scopes<api-nbi-getmappings-scopes>`)
    :param id: List of local ids
    :param remote_system: ID of Remote System (NOC settings)
    :param remote_id: List of IDs from Remote System
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:getmappings` API access.
    :statuscode 200: Success.
    :statuscode 400: Bad request.
    :statuscode 404: Object not found.
    :statuscode 500: Internal error.
