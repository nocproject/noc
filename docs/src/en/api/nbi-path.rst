.. _api-nbi-path:

============
NBI path API
============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

NBI path API allows to trace possible paths in discovered network
topology considering extra constraints.

.. _api-nbi-path-usage:

Usage
-----

.. http:post:: /api/nbi/path

    Trace k-shortest paths over network topology considering constraints.

    **Example Request**:

    .. sourcecode:: http

        POST /api/nbi/path  HTTP/1.1
        Host: noc.example.com
        Private-Token: 12345

        {
            "from": <path start specification>,
            "to": <path end specification>,
            "config": <path config specification>,
            "constraints": <path constraint specification>
        }

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/json

        {
            "status": true,
            "time": 0.012,
            "paths": [
                {
                    "path": [
                        {
                            "links": [
                                {
                                    "objects": [
                                        {
                                            "interfaces": [
                                                "Eth 1/27"
                                            ],
                                            "object": {
                                                "address": "172.11.101.209",
                                                "bi_id": 1362320908973547200,
                                                "id": 40046,
                                                "name": "sw1"
                                            }
                                        },
                                        {
                                            "interfaces": [
                                                "Eth 1/52"
                                            ],
                                            "object": {
                                                "address": "172.11.103.20",
                                                "bi_id": 6072199926162248000,
                                                "id": 17918,
                                                "name": "sw2"
                                            }
                                        }
                                    ]
                                },
                                ...
                            ]
                        },
                        ...
                    ],
                    "cost": {
                        "l2": 6
                    }
                },
                ...
            ]
        }

    :<json object from: :ref:`api-nbi-path-from`
    :<json object to: :ref:`api-nbi-path-to`
    :<json object config: :ref:`api-nbi-path-config`
    :<json object constraints: :ref:`api-nbi-path-constraints`
    :>json boolean status: Request status, `true` if success
    :>json string error: Error text, only if `status` is `false`.
    :>json float time: Request processing time in seconds.
    :>json array paths: Paths found, only if `status` is `true`.
    :reqheader Private-Token: :ref:`reference-apikey` with `nbi:path` API access
    :statuscode 200: Success

.. _api-nbi-path-from:

Path Start Specification
------------------------

Path Start specified as value of `from` request key and can be
either Managed Object, interface or service reference.

Managed Object By Id
^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "object": {
            "id": 12345
        }
    }

Where `12345` is the :ref:`reference-managed-object` Id

Managed Object By Id and Interface Name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "object": {
            "id": 12345
        },
        "interface": {
            "name": "Gi 0/1"
        }
    }

Where `12345` is the :ref:`reference-managed-object` Id and `Gi O/1`
is the normalized interface name.

Managed Object By Remote Id
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "object": {
            "remote_system": "6789",
            "remote_id": "1011"
        }
    }

Where `6789` is the :ref:`reference-remote-system` Id and
`1011` is the :ref:`reference-managed-object` Id in Remote System.

Managed Object By Remote Id and Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "object": {
            "remote_system": "6789",
            "remote_id": "1011"
        },
        "interface": {
            "name": "Gi 0/1"
        }
    }

Where `6789` is the :ref:`reference-remote-system` Id,
`1011` is the :ref:`reference-managed-object` Id in Remote System
and `Gi O/1` is the normalized interface name.

Interface by Id
^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "interface": {
            "id": "1234567"
        }
    }

Where `1234567` is the Interface Id

Service by Id
^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "service": {
            "id": 12345
        }
    }

Where `12345` is the :ref:`reference-service` Id

Service by Remote Id
^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "service": {
            "remote_system": "6789",
            "remote_id": "1011"
        }
    }

Where `6789` is the :ref:`reference-service` Id and
`1011` is the :ref:`reference-service` Id in Remote System.

Service by Order Id
^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "service": {
            "order_id": "1234"
        }
    }

Where `1234` is Order Fulfilment order id.
Or:

.. sourcecode:: json

    {
        "service": {
            "order_id": "1234",
            "remote_system": "5678"
        }
    }

The same, but restricted to remote system id `5678`

.. _api-nbi-path-to:

Path End Specification
----------------------

Path End specified as value of `to` request key.

* Explicit specification

  * Managed Object
  * Interface
  * Service

* Implicit specification

  * Object level


Managed Object By Id
^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "object": {
            "id": 12345
        }
    }

Where `12345` is the :ref:`reference-managed-object` Id

Managed Object By Id and Interface Name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "object": {
            "id": 12345
        },
        "interface": {
            "name": "Gi 0/1"
        }
    }

Where `12345` is the :ref:`reference-managed-object` Id and `Gi O/1`
is the normalized interface name.

Managed Object By Remote Id
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "object": {
            "remote_system": "6789",
            "remote_id": "1011"
        }
    }

Where `6789` is the :ref:`reference-remote-system` Id and
`1011` is the :ref:`reference-managed-object` Id in Remote System.

Managed Object By Remote Id and Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "object": {
            "remote_system": "6789",
            "remote_id": "1011"
        },
        "interface": {
            "name": "Gi 0/1"
        }
    }

Where `6789` is the :ref:`reference-remote-system` Id,
`1011` is the :ref:`reference-managed-object` Id in Remote System
and `Gi O/1` is the normalized interface name.

Interface by Id
^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "interface": {
            "id": "1234567"
        }
    }

Where `1234567` is the Interface Id

Service by Id
^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "service": {
            "id": 12345
        }
    }

Where `12345` is the :ref:`reference-service` Id

Service by Remote Id
^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "service": {
            "remote_system": "6789",
            "remote_id": "1011"
        }
    }

Where `6789` is the :ref:`reference-service` Id and
`1011` is the :ref:`reference-service` Id in Remote System.

By Object Level
^^^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "level": 30
    }

Specify path end by reaching Managed Object :ref:`Level <reference-managed-object-profile-level>`
greater than specified.

.. _api-nbi-path-config:

Path Config Specification
-------------------------

Path Config specified as value of `config` request key.

.. sourcecode:: json

    {
        "max_depth": 10,
        "n_shortest": 2
    }

Where:

* `max_depth` - Restrict search depth up to `max_depth` nodes.
* `n_shortest` - Return up to `n_shortest` paths.

.. _api-nbi-path-constraints:

Path Constraints Specification
------------------------------

Path Constraints are specified as value of `constraints` request key.

Explicit VLAN
^^^^^^^^^^^^^

..  sourcecode:: json

    {
        "vlan": {
            "vlan": 1234,
            "strict": false
        }
    }

Restrict paths to links having VLAN `1234`, either tagged or untagged.
`strict` parameter enforces additional checking:

* `true` - VLAN must be present on both sides of the link.
* `false` - VLAN must be present at least on one side of the link.

Implicit VLAN
^^^^^^^^^^^^^

.. sourcecode:: json

    {
        "vlan": {
            "interface_untagged": true,
            "strict": true
        }
    }

Get untagged vlan from start of path interface and restrict path
to links having this VLAN, either tagged or untagged.

`strict` parameter enforces additional checking:

* `true` - VLAN must be present on both sides of the link.
* `false` - VLAN must be present at least on one side of the link.

Upward Direction
^^^^^^^^^^^^^^^^
.. sourcecode:: json

    {
        "upwards": true
    }

Forces upward direction of path.
i.e. Managed Object :ref:`Level <reference-managed-object-profile-level>`
of each next object of the path may not be less that level of current
object. Effectively speed-ups path finding by denying descending to
lower levels of networks.
