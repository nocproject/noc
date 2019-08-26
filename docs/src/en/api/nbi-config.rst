.. _api-nbi-config:

==============
NBI config API
==============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

NBI config API allows remote system to fetch Managed Object's
configuration, eigther last of specified revision

.. _api-nbi-config-usage:

Usage
-----

Get last config
^^^^^^^^^^^^^^^

.. http:get:: /api/nbi/config/(int:object_id)

    Get last configuration for Managed Object with id `object_id`

    **Example Request**

    .. sourcecode:: http

        GET /api/nbi/config/333 HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/plain

        !
        hostname Switch
        ...

    :param object_id: Managed Object's id.
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:config` API access.
    :statuscode 200: Success.
    :statuscode 204: No Content. Config has not been read yet.
    :statuscode 404: Object not found.

Get config by revision
^^^^^^^^^^^^^^^^^^^^^^

.. http:get:: /api/nbi/config/(int:object_id)/(str:revision id)

    Get configuration revision `revision_id`
    for Managed Object with id `object_id`

    **Example Request**

    .. sourcecode:: http

        GET /api/nbi/config/333/5c03cb4cc04567000830be73 HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/plain

        !
        hostname Switch
        ...

    :param object_id: Managed Object's id
    :param revision: Config revision. Can be obtained via :ref:`configrevisions API<api-nbi-configrevisions>`
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:config` API access
    :statuscode 200: Success
    :statuscode 404: Object or revision not found
