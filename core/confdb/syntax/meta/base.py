# ----------------------------------------------------------------------
# ConfDB meta syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..defs import DEF
from ..patterns import ANY, INTEGER, IP_ADDRESS, CHOICES

META_SYNTAX = DEF(
    "meta",
    [
        DEF("id", [DEF(ANY, name="id", required=True, gen="make_meta_id")]),
        DEF("profile", [DEF(ANY, name="profile", required=True, gen="make_meta_profile")]),
        DEF("vendor", [DEF(ANY, name="vendor", required=True, gen="make_meta_vendor")]),
        DEF("platform", [DEF(ANY, name="platform", required=True, gen="make_meta_platform")]),
        DEF("version", [DEF(ANY, name="version", required=True, gen="make_meta_version")]),
        DEF(
            "object-profile",
            [
                DEF("id", [DEF(ANY, name="id", required=True, gen="make_meta_object_profile_id")]),
                DEF(
                    "name",
                    [DEF(ANY, name="name", required=True, gen="make_meta_object_profile_name")],
                ),
                DEF(
                    "level",
                    [
                        DEF(
                            INTEGER,
                            name="level",
                            required=True,
                            gen="make_meta_object_profile_level",
                        )
                    ],
                ),
            ],
        ),
        DEF(
            "segment",
            [
                DEF("id", [DEF(ANY, name="id", required=True, gen="make_meta_segment_id")]),
                DEF("name", [DEF(ANY, name="name", required=True, gen="make_meta_segment_name")]),
            ],
        ),
        DEF(
            "management",
            [
                DEF(
                    "address",
                    [
                        DEF(
                            IP_ADDRESS,
                            name="address",
                            required=True,
                            gen="make_meta_management_address",
                        )
                    ],
                ),
                DEF(
                    "protocol",
                    [
                        DEF(
                            CHOICES("telnet", "ssh", "http"),
                            name="protocol",
                            required=True,
                            gen="make_meta_management_protocol",
                        )
                    ],
                ),
            ],
        ),
        DEF("tags", [DEF(ANY, name="tag", required=True, multi=True, gen="make_meta_tag")]),
        DEF(
            "chassis_id",
            [
                DEF(
                    INTEGER,
                    [
                        DEF(
                            "range",
                            [
                                DEF(
                                    ANY,
                                    [
                                        DEF(
                                            ANY,
                                            name="mac2",
                                            required=True,
                                            gen="make_meta_chassis_id_mac2",
                                        )
                                    ],
                                    name="mac1",
                                    required=True,
                                    gen="make_meta_chassis_id_mac1",
                                ),
                            ],
                        ),
                    ],
                    name="n",
                    multi=True,
                    required=True,
                ),
            ],
        ),
        DEF(
            "matchers",
            [DEF(ANY, name="matcher", required=True, multi=True, gen="make_meta_matcher")],
        ),
    ],
)
