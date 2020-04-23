# ----------------------------------------------------------------------
# ConfDB system syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..defs import DEF
from ..patterns import ANY, CHOICES, HHMM, INTEGER

SYSTEM_SYNTAX = DEF(
    "system",
    [
        DEF("hostname", [DEF(ANY, required=True, name="hostname", gen="make_hostname")]),
        DEF("domain-name", [DEF(ANY, required=True, name="domain_name", gen="make_domain_name")]),
        DEF("prompt", [DEF(ANY, required=True, name="prompt", gen="make_prompt")]),
        DEF(
            "clock",
            [
                DEF(
                    "timezone",
                    [
                        DEF(
                            ANY,
                            [
                                DEF(
                                    "offset",
                                    [
                                        DEF(
                                            HHMM,
                                            required=True,
                                            name="tz_offset",
                                            gen="make_tz_offset",
                                        )
                                    ],
                                )
                            ],
                            required=True,
                            name="tz_name",
                            gen="make_tz",
                        )
                    ],
                    required=True,
                ),
                DEF(
                    "source",
                    [
                        DEF(
                            CHOICES("local", "ntp"),
                            name="source",
                            required=True,
                            gen="make_clock_source",
                        )
                    ],
                ),
            ],
        ),
        DEF(
            "user",
            [
                DEF(
                    ANY,
                    [
                        DEF("uid", [DEF(INTEGER, required=True, name="uid", gen="make_user_uid")]),
                        DEF(
                            "full-name",
                            [DEF(ANY, required=True, name="full_name", gen="make_user_full_name")],
                        ),
                        # enable level 15 should be encoded as `level-15`
                        DEF(
                            "class",
                            [
                                DEF(
                                    ANY,
                                    required=True,
                                    multi=True,
                                    name="class_name",
                                    gen="make_user_class",
                                )
                            ],
                        ),
                        DEF(
                            "authentication",
                            [
                                DEF(
                                    "encrypted-password",
                                    [
                                        DEF(
                                            ANY,
                                            required=True,
                                            name="password",
                                            gen="make_user_encrypted_password",
                                        )
                                    ],
                                ),
                                DEF(
                                    "ssh-rsa",
                                    [
                                        DEF(
                                            ANY,
                                            required=True,
                                            multi=True,
                                            name="rsa",
                                            gen="make_user_ssh_rsa",
                                        )
                                    ],
                                ),
                                DEF(
                                    "ssh-dsa",
                                    [
                                        DEF(
                                            ANY,
                                            required=True,
                                            multi=True,
                                            name="dsa",
                                            gen="make_user_ssh_dsa",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                    multi=True,
                    name="username",
                )
            ],
        ),
    ],
)
