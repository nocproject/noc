========
Workflow
========
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

*Workflow* is an abstract representation of real *Work* or *Process*.
*Workflow* may refer to *Managed Object*, *Service*, *Physical* and
*Logical Resource* that is being transferred from one *State* to another.
*Workflow* describes lifetime cycle of given *Resource* as finite
set of *States*. Every time *Resource* must be exactly in one *State*,
referred as *Current State*. *Current State* cannot be changed in
arbitrary fashion. Instead, *Workflow* defines possible *Transitions*
between *States*. So *Workflow* may be considered as `Directed Graph`_,
where *States* are vertices, and *Transitions* are edges.

*Workflows* are attached to *Resources* via *Profiles*. Resources
of same type may have different *Workflows*. i.e. "Customer VLAN"
and "Management VLAN" VLAN Profiles may use different *Workflows*.

.. _Directed Graph: https://en.wikipedia.org/wiki/Directed_graph

.. _reference-workflow-state:

State
-----
*State* is the single distingushed state in *Resource's* lifetime.

.. _reference-workflow-state-default-state:

Default State
~~~~~~~~~~~~~
One and only one *State* of *Workflow* must be marked as *Default State*.
NOC automatically assigns *Default State* to new *Resources* when *State*
is not given explicitly. Proper *Workflow* determined via *Resource's*
*Profile*.

.. _reference-workflow-state-productive-state:

Productive State
~~~~~~~~~~~~~~~~
*State* may be marked as *Productive*.

::
    # Resource is in productive usage
    is_productive = BooleanField(default=False)

.. note::

    Further versions of NOC will use *Productive State* to indicate
    that *Managed Object* may be discovered and monitored

Liveness Tracking
~~~~~~~~~~~~~~~~~

::
    # Discovery should update last_seen field
    update_last_seen = BooleanField(default=False)

Expiration
~~~~~~~~~~
::
    # State time-to-live in seconds
    # 0 - infinitive TTL
    # >0 - Set *expired* field to now + ttl
    #      Send *expired* signal when TTL expired
    # Expiration may also be delayed by *update_expired* setting
    ttl = IntField(default=0)
    # Update ttl every time when object is discovered
    update_expired = BooleanField(default=False)

Handlers
~~~~~~~~

.. todo::
    Describe workflow state

::
    # Handler to be called on entering state
    on_enter_handlers = ListField(StringField())
    # Job to be started when entered state (jcls)
    # Job key will be <state id>-<resource model>-<resource id>
    job_handler = StringField()
    # Handlers to be called on leaving state
    on_leave_handlers = ListField(StringField())

.. _reference-workflow-transition:

Transition
----------
.. todo::
    Describe workflow transition

::
    workflow = PlainReferenceField(Workflow)
    from_state = PlainReferenceField(State)
    to_state = PlainReferenceField(State)
    is_active = BooleanField(default=True)
    # Event name
    # Some predefined names exists:
    # seen -- discovery confirms resource usage
    # expired - TTL expired
    event = StringField()
    # Text label
    label = StringField()
    # Arbbitrary description
    description = StringField()
    # Enable manual transition
    enable_manual = BooleanField(default=True)
    # Handler to be called on starting transitions
    # Any exception aborts transtion
    handlers = ListField(StringField())

Event
-----
.. todo::
    Describe workflow event
    as viable part of discovery integration

Handler
-------
.. todo::
    Describe workflow handler

.. todo::
    Describe handler order

Resource
--------
.. todo::
    Describe workflow resource

* Managed Object (WIP)
* Interface (WIP)
* Prefix (WIP)
* Address (WIP)
* SubInterface (WIP)
* Phone Range (WIP)
* Phone Number (WIP)
* DNS Zone (WIP)
* VPN
* :ref:`reference-vlan`
* Project (WIP)
* Subscriber (WIP)
* Supplier (WIP)
* Service (WIP)

Migration
---------
.. todo::
    Describe Workflow Migrations

Best Practices
--------------

Free State
~~~~~~~~~~

Ready State
~~~~~~~~~~~

Cooldown State
~~~~~~~~~~~~~~

Reserved State
~~~~~~~~~~~~~~

External Jobs
~~~~~~~~~~~~~

Device Configuration
~~~~~~~~~~~~~~~~~~~~

Examples
--------

Default Workflow
~~~~~~~~~~~~~~~~
.. mermaid::

    graph TD
        Ready

When *Process* considers the *Resource* has no designated states,
simple *Workflow* with one "Ready" *State* may be used.
NOC provides "Default" workflow out-of-the box.

Resource Default Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~
.. mermaid::

    graph TD
        Free -->|reserve| Reserved
        Free -->|seen| Ready
        Reserved -->|expired| Free
        Reserved -->|approve| Approved
        Approved -->|seen| Ready
        Ready -->|suspend| Suspended
        Ready -->|expired| Cooldown
        Suspended -->|resume| Ready
        Cooldown -->|seen| Ready
        Cooldown -->|expired| Free

