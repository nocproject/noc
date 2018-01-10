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
* Configuration generation and checking

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
Segment is the set of *Managed Objects* and links between them so
it can be considered a *Graph*. NOC extends Graph with all *Managed Objects*
from adjacent segments, connected to given segment to build
*Segment Topology*. NOC automatically recognizes following topologies

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

.. _network-segment-topology-ring:

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

.. _network-segment-topology-mesh:

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

.. _networksegment-vlan-domains:

VLAN Domains
------------
*Network Segments* are closely tied with *VLAN* concept. VLANs are
not obliged to be network-wise, so VLAN 100 in one part of network
may not be same VLAN 100 from other part so VLAN space may be *overlapped*.
Unlike IPv4/IPv6 address space, which uses *VRF* to deal with address
space overlaps, 802.1 set of standards do not introduce global
distingueisher for VLAN space. So NOC uses concept of *VLAN Domain*.
*VLAN Domain*, shortly, is an area with unique VLAN space.
So VLAN 100 from different domains is not same VLAN 100, while
VLAN 100 on differen *Managed Objects* from same VLAN domain may
be considered same VLAN 100

For clearance and ease of maintenance NOC considers *VLAN Domain*
as a part of segment hierarchy. NOC uses *VLAN border* mark on segment
to split segments tree to *VLAN Domain*. *VLAN Domain* covers
*VLAN border* segment and all its descendants until next VLAN border.

Consider example:

.. mermaid::

    graph TB
        style S1 stroke-width:4px
        style S6 fill:#0f0,stroke-width:4px
        style S10 fill:#0f0
        style S11 fill:#0f0
        S1 --- S2
        S1 --- S3
        S1 --- S4
        S2 --- S5
        S2 --- S6
        S3 --- S7
        S3 --- S8
        S4 --- S9
        S6 --- S10
        S6 --- S11

VLAN borders marked by thick frame: S1 and S6. First VLAN domain (blue)
consist of S1, S2, S3, S4, S5, S7, S8 and S9. Second VLAN domain (green):
S6, S10 and S11. Though S6 is descendant of S1 it is marked as VLAN border,
so it starts its own domain.

.. note::
    Though *VLAN domains* are groups of *Network Segments* and
    *VLAN domain* is a set of *Managed Object*, empty network segments
    can be attached to *Subinterfaces*, so one *Managed Object* can
    still handle multiple *VLAN domains*

For ease of maintenance NOC automatically attaches all *VLAN domain's*
VLANs to appropriative *VLAN border*.

.. _network-segment-vlan-translation:

VLAN Translation
----------------
NOC consider any implicit VLAN passing stops at *VLAN border*. Though it
possible to propagate VLAN further via *VLAN Translation Rules*.
Consider scheme:

.. mermaid::

    graph TB
        style S1 stroke-width:4px
        style S2 fill:#0f0,stroke-width:4px
        S1 --- S2

S1 and S2 both *VLAN borders*. *Managed Objects* MO1 and MO2 belongs to
S1 and S2 respectively.

*VLAN Translation Rules* are defined at *VLAN border* segments as a list
of rules. Each rule contains following fields:

* filter: :doc:`/reference/vc-filter`
* rule: king of operation
* parent_vlan: reference to VLAN from parent segment

Rules are processed in definition order. First matching rule wins.

NOC supports two kind of rules: *Map* and *Push*.

Map
^^^
*Map* rule converts VLAN 802.1Q tag from target *VLAN domain* to
802.1Q tag from parent's segment.

VLANs can be either *rewritten*

.. mermaid::
    :caption: filter=2-200,rule=map,parent_vlan=200

    sequenceDiagram
        MO1 ->> Border: Tag=100
        Border ->> MO2: Tag=200

Or *extended* (rewritten to same tag)

.. mermaid::
    :caption: filter=2-200,rule=map,parent_vlan=100

    sequenceDiagram
        MO1 ->> Border: Tag=100
        Border ->> MO2: Tag=100

Push
^^^^
*Push* rule appends additional 802.1Q tag in top of existing 802.1Q tag,
allowing Q-in-Q tunneling.

.. mermaid::
    :caption: filter=2-200,rule=push,parent_vlan=300

    sequenceDiagram
        MO1 ->> Border: Tag=100
        Border ->> MO2: Tag=300,100

.. _network-segment-vlan-allocation-group:

VLAN Allocation Group
---------------------
.. todo::
    Describe VLAN allocation group

.. _network-segment-mac-discovery:

MAC Discovery
-------------
MAC topology discovery can be used as last resort when other
methods are failed. Contrary to other per-object methods MAC
discovery performed is per-segment basis using previously collected
MAC addresses. See :ref:`discovery-segment-mac` for details.

.. _network-segment-autosegmentation:

Autosegmentation
----------------
Segmentation may be performed automatically during box discovery.
See :ref:`discovery-box-segmentation` for details

.. _network-segment-redundancy:

Redundancy
----------
:ref:`network-segment-topology-ring` and :ref:`network-segment-topology-mesh`
offer path redundancy. NOC detects segment redundancy automatically.
Outages in redundant segments can leave to *Lost of Redundancy*.
*Lost of Redundancy* means that currently working services are left
without proper redundancy and are at risk in case of following outage.
During the outage NOC calculates affected services and services
with *Lost of Redundancy* and provides information to escalated
*Trouble Tickets*.

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
Network Segment's L2 MTU is minimal ethernet payload size guaranteed
to pass via Segment. MTU is accounted without 802.3 ethernet header
but with all other encapsulation headers (802.1Q, MPLS, etc).

Common L2 MTU values

====== =================================================================
L2 MTU Description
====== =================================================================
1500   Common untagged ethernet packet
1504   802.1Q VLAN tagged packet
1508   Q-in-Q packet
1536   MPLS packet with up to 3 labels
<1600  Baby giant
>1600  Jumbo
====== =================================================================

Understanding real segment's L2 MTU is viable part of providing effective
ethernet transit services. Transit interface with improper MTU may lead
to occasional packet drops. Such drops can lead to hard-to-diagnose
disruption of services.

.. note::
    Automatic detection of segment's L2 MTU is work-in-progress
    See :issue:`#624 <624>` for details

Network Map Settings
--------------------
.. todo::
    # Collapse object's downlinks on network map
    # when count is above the threshold
    max_shown_downlinks = IntField(default=1000)
