=======================
Network Segment Profile
=======================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Network Segment Profile is a group settings for :doc:`/reference/network-segment`

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
