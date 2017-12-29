===============
Network Segment
===============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Large networks tend to be hierarchical by nature, separating to various
layers. i. e. core, aggregation, access e.t.c. Therefore the network can
be considered as hierarchy of interconnected parts, called
*Network Segments*.

Network Segment is a group of :doc:`Managed Objects</reference/managed-object>`
taking specific part in network hierarchy. Each Managed Object *MUST*
belong to one Network Segment. Typical Network Segment hierarchy:

.. mermaid::

    graph TB
        CORE(Core)
        AGG1(Aggregation #1)
        AGG2(Aggregation #2)
        ACC11(Access #1-1)
        ACC12(Access #1-2)
        ACC21(Access #2-1)
        ACC22(Access #2-2)
        CORE -> AGG1
        CORE -> AGG2
        AGG1 -> ACC11
        AGG1 -> ACC12
        AGG2 -> ACC21
        AGG2 -> ACC22

.. note::

    NOC considers that is Managed Object belongs to segment, not the link.
    So in terms of network separation NOC uses IS-IS approach, not OSPF one.

Each segment except top-level ones has exactly one *Parent* and has
zero-or-more *Children* segments. So segment provides connectivity
between its children and the rest of network.

Proper segmentation is the key concept for various areas:

* Root-Cause Analysis (RCA) for Fault Management
* Network Maps
* VLAN management

.. note::

    NOC considers that proper segmentation is performing during network
    design and planning stage. Sometimes it's not true and segmentation
    is *implicit* or *ad-hoc*. Despite it considered *Bad Practice*
    NOC offers various methods for :ref:`automatical segmentation<network-segment-autosegmentation>`


Group Settings
--------------
Group settings for Network Segments are contained in :doc:`/reference/network-segment-profile`

.. _network-segment-segment-topology:

Segment Topology
----------------

Tree
^^^^
Tree topology contains exactly one path between any Object.

.. mermaid::

    graph TB
        MO1 -> MO2
        MO1 -> MO3
        MO1 -> MO4
        MO2 -> MO5
        MO2 -> MO6
        MO6 -> MO7
        MO3 -> MO8
        MO3 -> MO9
        MO4 -> MO10
        MO4 -> MO11
        MO10 -> MO12

*Tree* offers no redundancy. Any failed Object makes its children
unavailable. Following example shows failed *MO3* makes *MO8* and *MO9*
unavailable.

.. mermaid::

    graph TB
        style MO3 fill:#c0392b
        style MO8 fill:#7f8c8d
        style MO9 fill:#7f8c8d
        MO1 -> MO2
        MO1 -> MO3
        MO1 -> MO4
        MO2 -> MO5
        MO2 -> MO6
        MO6 -> MO7
        MO3 -> MO8
        MO3 -> MO9
        MO4 -> MO10
        MO4 -> MO11
        MO10 -> MO12

NOC performs auto-layout of *Tree* segment maps and proper RCA

Forest
^^^^^^
*Forest* is common case with two-or-more independ trees. Like a *Tree*
*Forest* offers no redundancy. Any failed Object makes its children
unavailable.
NOC performs auto-layout of *Forest* segment maps and proper RCA

Ring
^^^^
Common *Ring* topology considers each object connected with exactly two
neighbors

.. mermaid::

    graph TB
        MO1 -> MO2
        MO2 -> MO3
        MO3 -> MO4
        MO5 -> MO6
        MO6 -> MO7
        MO7 -> MO4

*Ring* offers protection against single node failure. Following example
shows *MO3* failure not affects other objects

.. mermaid::

    graph TB
        style MO3 fill:#c0392b
        MO1 -> MO2
        MO2 -> MO3
        MO3 -> MO4
        MO5 -> MO6
        MO6 -> MO7
        MO7 -> MO4

Though additional failure of *MO7* leads to *MO4* unavailability

.. mermaid::

    graph TB
        style MO3 fill:#c0392b
        style MO7 fill:#c0392b
        style MO4 fill:#7f8c8d
        MO1 -> MO2
        MO2 -> MO3
        MO3 -> MO4
        MO5 -> MO6
        MO6 -> MO7
        MO7 -> MO4

Pure *Ring* topology is rather expensive, as any Object must be
capable of forwarding all ring's traffic and is not very flexible
to expanding port space. So real networks tends to use combined *Ring* and
*Tree* topology, while segment's backbone is the common *Ring* combined
with small *expansion trees*, attached to *Ring* nodes. Port expansion
is performed with cheap switches contained within same PoP with backbone nodes.

.. todo::
    Show Ring-and-Tree topology and describe fault propagation

NOC performs neat auto-layout of *Ring* segment maps and proper RCA

Mesh
^^^^
*Mesh* is the common graph which is not *Tree*, *Forest* or *Ring*

.. mermaid::

    graph TB
        MO1 -> MO2
        MO1 -> MO3
        MO2 -> MO3
        MO3 -> MO4
        MO4 -> MO5
        MO1 -> MO5

NOC performs probabilistic spring layout for mesh networks and perform
proper RCA in most cases

.. _network-segment-horizontal-transit:

Horizontal Transit
------------------
    # Horizontal transit policy
    horizontal_transit_policy = StringField(
        choices=[
            ("E", "Always Enable"),
            ("C", "Calculate"),
            ("D", "Disable"),
            ("P", "Profile")
        ], default="P"
    )
    # Horizontal transit settings
    # i.e. Allow traffic flow not only from parent-to-childrens and
    # children-to-children, but parent-to-parent and parent-to-neighbors
    # Calculated automatically during topology research
    enable_horizontal_transit = BooleanField(default=False)

.. _network-segment-object-uplinks:

Object Uplinks
--------------

.. mermaid::

    graph TB
        MO1 -> MO2
        MO1 -> MO3
        MO2 -> MO4
        MO3 -> MO4

.. _network-segment-sibling-segments:

Sibling Segments
----------------

VLAN Domains
------------
    # VLAN namespace demarcation
    # * False - share namespace with parent VLAN
    # * True - split own namespace
    vlan_border = BooleanField(default=True)
    # VLAN translation policy when marking border
    # (vlan_border=True)
    # Dynamically recalculated and placed to VLAN.translation_rule
    # and VLAN.parent
    vlan_translation = ListField(EmbeddedDocumentField(VLANTranslation))

VLAN Allocation Group
---------------------

.. _network-segment-mac-discovery:

MAC Discovery
-------------

.. _network-segment-autosegmentation:

Autosegmentation
----------------

.. _network-segment-redudancy:

Redudancy
---------
    # True if segment has alternative paths
    is_redundant = BooleanField(default=False)
    # True if segment is redundant and redundancy
    # currently broken
    lost_redundancy = BooleanField(default=False)

.. _network-segment-settings:

Object Settings
---------------

Segments can hold Managed Object's recommended settings for config generation
and validation Settings can be either scalar (defined once)
or list (can be declared multiple times).
Omitted settings are inherited from parent segment, allowing to define
global settings at top level and refine them on lower levels

================= ===== ====================================================
Key               Multi Description
================= ===== ====================================================
domain_name       No    Default domain name
dns               Yes   DNS server's address
ntp               Yes   NTP server's address
default_gw        No    Default gateway for management network
syslog_collector  Yes   SYSLOG collector's address
snmp_collector    Yes   SNMP Trap collector's address
aaa_radius        Yes   RADIUS AAA server's address used for authentication
radius_collector  Yes   RADIUS collector's address
aaa_tacacs        Yes   TACACS+ AAA server's address used for authentication
tacacs_collector  Yes   TACACS+ collector's address
netflow_collector Yes   NetFlow collector's address
================= ===== ====================================================

L2 MTU
------
    # Provided L2 MTU
    l2_mtu = IntField(default=1504)

Network Map Settings
--------------------
    # Collapse object's downlinks on network map
    # when count is above the threshold
    max_shown_downlinks = IntField(default=1000)
