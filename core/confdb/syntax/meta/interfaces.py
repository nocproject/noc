# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB interfaces X meta syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ..defs import DEF
from ..patterns import ANY, INTEGER

INTERFACES_META_SYNTAX = DEF(
    "meta",
    [
        DEF("mac", [DEF(INTEGER, name="mac", required=True, gen="make_interfaces_meta_mac")]),
        DEF(
            "ifindex",
            [DEF(INTEGER, name="ifindex", required=True, gen="make_interfaces_meta_ifindex")],
        ),
        DEF(
            "profile",
            [
                DEF(
                    "id",
                    [DEF(ANY, name="id", required=True, gen="make_interfaces_meta_profile_id")],
                ),
                DEF(
                    "name",
                    [DEF(ANY, name="name", required=True, gen="make_interfaces_meta_profile_name")],
                ),
            ],
        ),
        DEF(
            "link",
            [
                DEF(
                    ANY,
                    [
                        DEF(
                            "object",
                            [
                                DEF(
                                    "id",
                                    [
                                        DEF(
                                            ANY,
                                            name="object_id",
                                            required=True,
                                            gen="make_interfaces_meta_link_object_id",
                                        )
                                    ],
                                ),
                                DEF(
                                    "name",
                                    [
                                        DEF(
                                            ANY,
                                            name="object_name",
                                            required=True,
                                            gen="make_interfaces_meta_link_object_name",
                                        )
                                    ],
                                ),
                                DEF(
                                    "profile",
                                    [
                                        DEF(
                                            "id",
                                            [
                                                DEF(
                                                    ANY,
                                                    name="id",
                                                    required=True,
                                                    gen="make_interfaces_meta_link_object_profile_id",
                                                )
                                            ],
                                        ),
                                        DEF(
                                            "name",
                                            [
                                                DEF(
                                                    ANY,
                                                    name="name",
                                                    required=True,
                                                    gen="make_interfaces_meta_link_object_profile_name",
                                                )
                                            ],
                                        ),
                                        DEF(
                                            "level",
                                            [
                                                DEF(
                                                    INTEGER,
                                                    name="level",
                                                    required=True,
                                                    gen="make_interfaces_meta_link_object_profile_level",
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        DEF(
                            "interface",
                            [
                                DEF(
                                    ANY,
                                    name="remote_interface",
                                    required=True,
                                    multi=True,
                                    gen="make_interfaces_meta_link_interface",
                                )
                            ],
                        ),
                    ],
                    name="link",
                    multi=True,
                )
            ],
        ),
    ],
)
