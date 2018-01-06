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
        CORE --- AGG1
        CORE --- AGG2
        AGG1 --- ACC11
        AGG1 --- ACC12
        AGG2 --- ACC21
        AGG2 --- ACC22

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
        MO1 --- MO2
        MO1 --- MO3
        MO1 --- MO4
        MO2 --- MO5
        MO2 --- MO6
        MO6 --- MO7
        MO3 --- MO8
        MO3 --- MO9
        MO4 --- MO10
        MO4 --- MO11
        MO10 --- MO12

*Tree* offers no redundancy. Any failed Object makes its children
unavailable. Following example shows failed *MO3* makes *MO8* and *MO9*
unavailable.

.. mermaid::

    graph TB
        style MO3 fill:#c0392b
        style MO8 fill:#7f8c8d
        style MO9 fill:#7f8c8d
        MO1 --- MO2
        MO1 --- MO3
        MO1 --- MO4
        MO2 --- MO5
        MO2 --- MO6
        MO6 --- MO7
        MO3 --- MO8
        MO3 --- MO9
        MO4 --- MO10
        MO4 --- MO11
        MO10 --- MO12

NOC performs auto-layout of *Tree* segment maps and proper RCA

Forest
^^^^^^
*Forest* is common case with two-or-more independ trees. Like a *Tree*

.. mermaid::

    graph TB
        MO1 --- MO4
        MO1 --- MO5
        MO5 --- MO6
        MO2 --- MO7
        MO2 --- MO8
        MO3 --- MO9
        MO3 --- MO10
        MO9 --- MO11

*Forest* offers no redundancy. Any failed Object makes its children
unavailable.
NOC performs auto-layout of *Forest* segment maps and proper RCA

.. note::

    *Forest* segments should be split to several *Tree* segment
    unless you have explicit reason to use *Forest*

Ring
^^^^
Common *Ring* topology considers each object connected with exactly two
neighbors

.. mermaid::

    graph TB
        MO1 --- MO2
        MO1 --- MO5
        MO2 --- MO3
        MO3 --- MO4
        MO5 --- MO6
        MO6 --- MO4

*Ring* offers protection against single node failure. Following example
shows *MO3* failure not affects other objects

.. mermaid::

    graph TB
        style MO3 fill:#c0392b
        MO1 --- MO2
        MO1 --- MO5
        MO2 --- MO3
        MO3 --- MO4
        MO5 --- MO6
        MO6 --- MO4

Though additional failure of *MO6* leads to *MO4* unavailability

.. mermaid::

    graph TB
        style MO3 fill:#c0392b
        style MO6 fill:#c0392b
        style MO4 fill:#7f8c8d
        MO1 --- MO2
        MO1 --- MO5
        MO2 --- MO3
        MO3 --- MO4
        MO5 --- MO6
        MO6 --- MO4

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
        MO1 --- MO2
        MO1 --- MO3
        MO2 --- MO3
        MO3 --- MO4
        MO4 --- MO5
        MO1 --- MO5

NOC performs probabilistic spring layout for mesh networks which may
require manual correction and performs proper RCA in most cases

.. _network-segment-object-uplinks:

Object Uplinks
--------------
While *Network Segments* establish network's hierarchy, almost each
segment obtains one direct *Parent Segment*. Each of segment's
*Managed Objects* should have one or more *Paths* to *Parent Segment*
in order to establish *Connectivity* with all network. Those paths
are called *Uplink Paths* and all direct *Neighbors* along the *Uplink Path*
considered *Uplinks*. The role of *Uplink* is to provide *Connectivity*
to its *Downlinks*. For reserved topologies object's *Uplink* may be
its *Downlink* at the same time.

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

*Uplinks* are key concept for *Topology-based Root-cause Analysis*.
If all object's uplinks are unavailable, object's unavailability
is *Consequence* of uplinks' failure. This is why correct segmentation
and link detection is necessary for proper RCA.

NOC rebuilds uplinks map for segment automatically every time
*Managed Object* joins or leaves segment or segment topology changed.
It is advised to avoid very large segments (>100 Objects)

.. _network-segment-horizontal-transit:

Horizontal Transit
------------------
Sometimes network segments of same level connected together
for backup purposes. So in case of uplink failure one segment
can use other as temporary uplink (*S2* - *S3* dotted link).

.. mermaid::

    graph TB
        S1 --- S2
        S1 --- S3
        S2 -.- S3

NOC offers additional Network Segment setting to specify whether
such horizontal traffic flow is acceptable. *Horizontal Transit Policy*
configured on per-segment and per- Network Segment Profile basis via
*Horizontal Transit Policy* setting. Possible values are:

* **Profile** (default): Use *Horizontal Transit Policy* from Network Segment Profile.
* **Always Enable**: *Horizontal Transit* is always enabled.
* **Disable**: *Horizontal Transit* is always disabled.
* **Calculate**: *Horizontal Transit* is enabled if horizontal link is present

NOC adjust RCA behavior in according to *Horizontal Transit Policy*,
considering neighbor segment as additional *Uplink Path*.

.. _network-segment-sibling-segments:

Sibling Segments
----------------
Network topology may change over time. Consider typical scheme
of broadband access network:

.. mermaid::

    graph TB
        subgraph Parent
        AGG1
        end
        subgraph ODF
        P1
        P2
        P3
        P4
        end
        subgraph Segment1
        MO11
        MO12
        MO13
        end
        subgraph Segment2
        MO21
        MO22
        MO23
        end
        AGG1 --- P1
        P1   --- MO11
        AGG1 --- P2
        P2   --- MO13
        MO11 --- MO12
        MO13 --- MO12
        AGG1 --- P3
        P3   --- MO21
        AGG1 --- P4
        P4   --- MO23
        MO21 --- MO22
        MO23 --- MO22

Two separate optic cables build two access ring and terminated on
four ports on aggregation switch. Consider we'd overestimated
demands on *Segment1* or on *Segment2* or on both of them and total
load on segments remains relatively low. Then we became short of
ports in *AGG1*. We'd decided to connect *MO13* and *MO21* directly
bypassing *AGG1*, so we'd disconnected two ports on *AGG1* and shorted
ports *P2* and *P3* on *ODF* by optical patch-cord:

.. mermaid::

    graph TB
        subgraph Parent
        AGG1
        end
        subgraph ODF
        P1
        P2
        P3
        P4
        end
        subgraph Segment1
        MO11
        MO12
        MO13
        end
        subgraph Segment2
        MO21
        MO22
        MO23
        end
        AGG1 --- P1
        P1   --- MO11
        P2   -.- P3
        P2   --- MO13
        MO11 --- MO12
        MO13 --- MO12
        P3   --- MO21
        AGG1 --- P4
        P4   --- MO23
        MO21 --- MO22
        MO23 --- MO22

Technically, we'd merged *Segment1* and *Segment2* building larger
segment. We can simple move *MO21*, *MO22* and *MO23* to *Segment1*
and eliminate *Segment2*. But sometimes is necessary to leave
*Segment1* and *Segment2* separation (lots of printed documentation,
maintenance service's habbits, reporting and direct links). NOC allows
to declare *Segment1* and *Segment2* as the *Sibling Segments*.
*Sibling Segments* considered as single segment in hierarchy,
processed as one in *Uplinks* calculations and shown as a single
map, though remaining two separate segments in database and reporting.

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
