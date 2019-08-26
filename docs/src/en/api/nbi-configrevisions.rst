.. _api-nbi-configrevisions:

=======================
NBI configrevisions API
=======================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

NBI configrevisions API allows remote system to fetch full history
of Managed Object's config revisions.

.. _api-nbi-configrevisions-usage:

Usage
-----

.. http:get:: /api/nbi/configrevisions/(int:object_id)

    Get all config revisions for Managed Object with id `object_id`

    **Example Request**

    .. sourcecode:: http

        GET /api/nbi/configrevisions/333 HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/json

        [
            {
                "timestamp":"2019-04-23T13:38:59.282000",
                "revision":"5c03cb4cc04567000830be73"
            },
            {
                "timestamp":"2018-05-20T08:09:42.953000",
                "revision":"5c03cb4cc04567000830be77"
            },
            {
                "timestamp":"2016-06-25T08:04:41",
                "revision":"5ca35f6aa2342e1516bf0cd7"
            }
        ]

    :param object_id: Managed Object's id
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:configrevisions` API access
    :statuscode 200: Success
    :statuscode 404: Object not found
