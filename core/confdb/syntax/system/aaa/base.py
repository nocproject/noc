# ----------------------------------------------------------------------
# ConfDB system AAA syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import ANY, CHOICES, IP_ADDRESS, INTEGER, VR_NAME, FI_NAME


SYSTEM_AAA_SYNTAX = DEF(
    "aaa",
    [
        DEF(
            "service",
            [
                DEF(
                    ANY,
                    [
                        DEF(
                            "type",
                            [
                                DEF(
                                    CHOICES("local", "radius", "tacacs+", "ldap", "ad"),
                                    name="type",
                                    required=True,
                                    gen="make_aaa_service_type",
                                )
                            ],
                        ),
                        DEF(
                            "address",
                            [
                                DEF(
                                    IP_ADDRESS,
                                    [
                                        DEF(
                                            "port",
                                            [
                                                DEF(
                                                    INTEGER,
                                                    name="port",
                                                    gen="make_aaa_service_address_port",
                                                )
                                            ],
                                        ),
                                        DEF(
                                            "source",
                                            [
                                                DEF(
                                                    IP_ADDRESS,
                                                    name="source_ip",
                                                    gen="make_aaa_service_address_source",
                                                )
                                            ],
                                        ),
                                        DEF(
                                            "virtual-router",
                                            [
                                                DEF(
                                                    VR_NAME,
                                                    [
                                                        DEF(
                                                            "forwarding-instance",
                                                            [
                                                                DEF(
                                                                    FI_NAME,
                                                                    name="fi",
                                                                    default="default",
                                                                    gen="make_aaa_service_fi",
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                    required=True,
                                                    name="vr",
                                                    default="default",
                                                )
                                            ],
                                        ),
                                        DEF(
                                            "timeout",
                                            [
                                                DEF(
                                                    INTEGER,
                                                    name="seconds",
                                                    gen="make_aaa_service_address_timeout",
                                                )
                                            ],
                                        ),
                                        DEF(
                                            "radius",
                                            [
                                                DEF(
                                                    "secret",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            name="secret",
                                                            gen="make_aaa_service_address_radius_secret",
                                                        )
                                                    ],
                                                ),
                                                DEF(
                                                    "radsec",
                                                    [
                                                        DEF(
                                                            "certificate",
                                                            [
                                                                DEF(
                                                                    ANY,
                                                                    name="certificate",
                                                                    gen="make_aaa_service_address_radius_radsec_certificate",
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        DEF(
                                            "tacacs+",
                                            [
                                                DEF(
                                                    "secret",
                                                    [
                                                        DEF(
                                                            ANY,
                                                            name="secret",
                                                            gen="make_aaa_service_address_tacacs_secret",
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                    name="ip",
                                    multi=True,
                                    gen="make_aaa_service_address",
                                )
                            ],
                        ),
                    ],
                    multi=True,
                    name="name",
                    gen="make_aaa_service",
                ),
                DEF("order", [DEF(ANY, multi=True, name="name", gen="make_aaa_service_order")]),
            ],
        )
    ],
)
