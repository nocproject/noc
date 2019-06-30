.. _release-19.3:

========
NOC 19.3
========

.. warning::

    Upcoming release

In accordance to our :ref:`Release Policy <releases-policy>`
`we're <https://getnoc.com/devteam/>`_ proudly present release `19.3 <https://code.getnoc.com/noc/noc/tags/19.3>`_.

19.3 release contains of
`??? <https://code.getnoc.com/noc/noc/merge_requests?scope=all&state=merged&milestone_title=19.3>`_
bugfixes, optimisations and improvements.

Highlights
----------

.. _release-19.3-rca-neighbor-cache:

Topology RCA Optimization
^^^^^^^^^^^^^^^^^^^^^^^^^
Topology-based Root-Cause analysis may be resource consumption.
NOC 19.3 introduces new experimental accelerated mode
called `RCA Neighbor Cache`. Smarter data precalculation and caching
in combination of database query optimization and bulk updates
allows to achieve 2-3 times speedup on real-world installations.

To enable the feature perform following steps:

* Run fix::

   $ noc fix apply fix_object_uplinks

* Stop :ref:`services-correlator` processes
* Enable :ref:`config-fm-enable_rca_neighbor_cache` configuration variable
* Start :ref:`services-correlator` processes

.. warning::

    Alarm processing will be postponed when correlator process is stopped,
    so alarm creation and clearing will be delayed until the correlator
    process will be started again.


Breaking Changes
----------------

.. _release-19.3-explicit-mongo-connect:

Explicit MongoDB Connections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Prior to 19.3 NOC relied that importing of `noc.lib.nosql` automatically
creates MongoDB connection. This kind of auto-magic is used to work
but requires to access all mongo-related stuff via `noc.lib.nosql`.
Starting from 19.3 we're beginning to cleanup API and the code and demand,
that MongoDB connection is to be initialized implicitly.

For custom commands and python scripts

.. code-block:: python

    from noc.core.mongo.connection import connect

    ...
    connect()


For custom services set service's `use_mongo` property to `True`

Other Changes
^^^^^^^^^^^^^
* ManagedObjectSelector.resolve_expression() renamed
  to ManagedObjectSelector.get_objects_from_expression()
