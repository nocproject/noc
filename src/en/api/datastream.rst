.. _api-datastream:

==========
DataStream
==========

.. toctree::
    :titlesonly:
    :glob:

    /api/datastream-*

DataStream is an universal API intended to stream database actual state
to external systems.

Streams
-------
DataStream supports multiple `streams` of changes. Each stream
may track actual versions of given type of objects. Each object
reflected in stream only once, though can be reordered in stream
while being changed.

.. _api-datastream-changeid:

Change ID
---------
Change ID is 24-character identifier of record's version. Every time
record changed it assigned with new Change ID. Change ID is time-based,
and later changes will lead to greater Change ID.

Following properties of Change ID are viable to understanding DataStream
powers:

*

.. _api-datastream-usage:

Usage
-----

.. http:get:: /api/datastream/(stream)

    Get datastream data for a `stream`. Result is a JSON array containing
    up to *limit* objects ordered by :ref:`Change ID<api-datastream-changeid>`.
    Each item is an object containing last actualized state.
    Empty reply in non-blocking mode (*block* == 0) means that all actualized
    changes is already transferred and client may stop and repeat request
    after a while.
    Connection timeout in blocking mode (*block* == 1) means aborted long polling
    due to timeout. Client should retry request immediately.

    **Example Request**:

    .. sourcecode:: http

        GET /api/datastream/administrativedomain?limit=1 HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

    **Example Response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/json
        X-NOC-DataStream-Limit: 1
        X-NOC-DataStream-First-Change: 1
        X-NOC-DataStream-Last-Change: 1
        X-NOC-DataStream-Total: 1

        [
            {
                ...
            }
        ]

    :query limit: Limit amount of records returned per one request. Note
        that DataStream service also applies its own configured limits.
    :query block: Enable/Disable long polling

        * 0 - do not block. Return empty list if no more changes available (default).
        * 1 - block until more changes became available.
    :query from: Return only results with greater :ref:`change id<api-datastream-changeid>`.
        Start from beginning if missed.
        ISO 8601 timestamp (i.e. YYYY-MM-DDTHH:MM:SS) may be used for time-based references.
    :query filter: Apply filter function. May be set multiple times.
        Filter functions may be global or datastream-specific. Examples:

        * filter=id(123)
        * filter=pool(default)&filter=shard(0,4)
    :reqheader Private-Token: :ref:`reference-apikey` with `datastream` API access
    :resheader X-NOC-DataStream-Limit: Actual records limit
    :resheader X-NOC-DataStream-First-Change: :ref:`change id<api-datastream-changeid>` of first change in response (Empty if no changes)
    :resheader X-NOC-DataStream-Last-Change: :ref:`change id<api-datastream-changeid>` of last change in response (Empty if no changes)
    :resheader X-NOC-DataStream-Total: Total amount of changes in response
    :statuscode 200: Success
    :statuscode 403: Permission Denied


Authentication
--------------
Common :ref:`reference-apikey` scheme is used for client authentication.
:ref:`datastream<_reference-apikey-roles-datastream>` API access required.

Scenarios
---------

Full Data Fetching
^^^^^^^^^^^^^^^^^^
Start from very start and process until stream contains changes

.. sourcecode::

    change_id = None
    while True:
      GET /api/datastream/<поток>?from={change_id}
      change_id = X-NOC-DataStream-Last-Change
      if not change_id:
        break
      for item in response:
          process_item(item)

Incremental Fetching
^^^^^^^^^^^^^^^^^^^^
Last processed :ref:`Change ID<api-datastream-changeid>` should
be stored somewhere and restored on next run. This scenario
offers gentle recover in case of `process_item` failure.

.. sourcecode::

    change_id = restore_change_id()
    while True:
      GET /api/datastream/<поток>?from={change_id}
      change_id = X-NOC-DataStream-Last-Change
      if not change_id:
        break
      for item in response:
          process_item(item)
          save_change_id(change_id)

Realtime Streaming
^^^^^^^^^^^^^^^^^^
Exploit `block=1` query parameter. Client will block awaiting new
changes. Note that http client may break request during timeout,
so code must catch timeout and repeat request

.. sourcecode::

    change_id = restore_change_id()
    while True:
      GET /api/datastream/<поток>?from={change_id}&block=1
      if timed_out:
          continue
      change_id = X-NOC-DataStream-Last-Change
      for item in response:
          process_item(item)
          save_change_id(change_id)

Record deletion processing
^^^^^^^^^^^^^^^^^^^^^^^^^^
Deleted records remains in stream and marked with `$deleted` key

.. sourcecode::

    {
      "id": "XXXXX",
      ...
      "$deleted": true
      ...
    }

.. _api-datastream-filters:

Filters
-------

Default filters set available to all DataStreams

.. function:: id(id)

    Restrict stream to object with given `id`

    :param id: Object id

.. function:: shard(instance, n_instances)

    Perform stream sharding, splitting stream to *n_instances*
    independed parts

    :param instance: Number of instance `[0 .. n_instances - 1]`
    :param n_instances: Total amount of instances
