===============
Network Segment
===============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 2
    :class: singlecol

.. todo::
    Describe common concepts

Group Settings
--------------
Group settings for Network Segments are contained in :doc:`/reference/network-segment-profile`

.. _network-segment-segment-topology:

Segment Topology
----------------

Tree
^^^^

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

Forest
^^^^^^

Ring
^^^^

.. mermaid::

    graph TB
        MO1 -> MO2
        MO2 -> MO3
        MO3 -> MO4
        MO5 -> MO6
        MO6 -> MO7
        MO7 -> MO4

Mesh
^^^^

.. mermaid::

    graph TB
        MO1 -> MO2
        MO1 -> MO3
        MO2 -> MO3
        MO3 -> MO4
        MO4 -> MO5
        MO1 -> MO5

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
