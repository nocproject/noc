.. _reference-network-segment-profile:

=======================
Network Segment Profile
=======================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Network Segment Profile is a group settings for :ref:`Network Segment<reference-network-segment>`

.. _reference-network-segment-profile-uplink-policy:

Uplink Policy
-------------
:ref:`Segment Uplinks <reference_network-segment-object-segment-uplinks>` calculation
is configured via *Uplink Policy* setting. *Uplink Policy* is the
list of methods in order of preference. NOC tries the methods one-by-one
until finds any appropriate Network Segment's uplinks.

Segment Hierarchy
^^^^^^^^^^^^^^^^^
*Connectivity* provided by parent segment. Uplinks are all objects
from parent segment having links to segment.

Consider the scheme:

.. mermaid::

    graph TB
        subgraph Parent
        MO1
        end
        subgraph Segment
        MO2
        MO3
        MO4
        end
        MO1 --- MO2
        MO1 --- MO3
        MO2 --- MO4
        MO3 --- MO4

Lets *MO1* belong to *Parent Segment*, while *MO2*, *MO3* and *MO4* are
in current *Segment*. The table of *Uplinks* and *Downlinks*:

======== ========= ===========
Object   Uplinks   Downlinks
======== ========= ===========
MO2      MO1, MO4  MO4
MO3      MO1, MO4  MO4
MO4      MO2, MO3  MO2, MO3
======== ========= ===========

Object Level
^^^^^^^^^^^^
Objects with greatest :ref:`level <reference-managed-object-profile-level>`
is elected as uplinks. Objects can belong both to segment and neighbor segments.

All Segment Objects
^^^^^^^^^^^^^^^^^^^
All Segment's Objects provide full network *Connectivity*. Any segment
neighbor is uplink.

Lesser Management Address
^^^^^^^^^^^^^^^^^^^^^^^^^
Segment's Object with lesser management address is elected as Uplink

Greater Management Address
^^^^^^^^^^^^^^^^^^^^^^^^^^
Segment's Object with greater management address is elected as Uplink

.. todo::

    Complete documentation
    name = StringField(unique=True)
    description = StringField(required=False)
    #
    discovery_interval = IntField(default=86400)
    # Restrict MAC discovery to management vlan
    mac_restrict_to_management_vlan = BooleanField(default=False)
    # Management vlan, to restrict MAC search for MAC topology discovery
    management_vlan = IntField(required=False, min_value=1, max_value=4095)
    # MVR VLAN
    multicast_vlan = IntField(required=False, min_value=1, max_value=4095)
    # Detect lost redundancy condition
    enable_lost_redundancy = BooleanField(default=False)
    # Horizontal transit policy
    horizontal_transit_policy = StringField(
        choices=[
            ("E", "Always Enable"),
            ("C", "Calculate"),
            ("D", "Disable")
        ], default="D"
    )
    # Default profile for autocreated children segments
    # (i.e. during autosegmentation)
    # Copy this segment profile otherwise
    autocreated_profile = PlainReferenceField("self")
    # List of enabled topology method
    # in order of preference (most preferable first)
    topology_methods = ListField(EmbeddedDocumentField(SegmentTopologySettings))
    # Enable VLAN discovery for appropriative management objects
    enable_vlan = BooleanField(default=False)
    # Default VLAN profile for discovered VLANs
    default_vlan_profile = PlainReferenceField("vc.VLANProfile")
