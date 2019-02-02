# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Normalized config syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import DEF, ANY

VR_NAME = ANY
FI_NAME = ANY
IF_NAME = ANY
UNIT_NAME = ANY
IF_UNIT_NAME = ANY
IPv4_ADDRESS = ANY
IPv4_PREFIX = ANY
IPv6_ADDRESS = ANY
IPv6_PREFIX = ANY
ISO_ADDRESS = ANY
NUMBER = ANY

SYNTAX = [
    DEF("system", [
        DEF("hostname", [
            DEF(ANY, required=True)
        ]),
        DEF("domain-name", [
            DEF(ANY, required=True)
        ]),
        DEF("prompt", [
            DEF(ANY, required=True)
        ]),
        DEF("clock", [
            DEF("timezone", [
                DEF(ANY, required=True)
            ], required=True)
        ])
    ]),
    DEF("virtual-router", [
        DEF(VR_NAME, [
            DEF("forwarding-instance", [
                DEF(FI_NAME, [
                    DEF("interface", [
                        DEF(IF_NAME, [
                            DEF("description", [
                                DEF(ANY, required=True)
                            ]),
                            DEF("unit", [
                                DEF(UNIT_NAME, [
                                    DEF(ANY, [
                                        DEF("description", [
                                            DEF(ANY, required=True)
                                        ]),
                                        DEF("inet", [
                                            DEF("address", [
                                                DEF(IPv4_PREFIX, multi=True)
                                            ])
                                        ]),
                                        DEF("inet6", [
                                            DEF("address", [
                                                DEF(IPv6_PREFIX, multi=True)
                                            ])
                                        ]),
                                        DEF("iso", [
                                            DEF("address", [
                                                DEF(ISO_ADDRESS, multi=True)
                                            ])
                                        ]),
                                        DEF("bridge", [
                                            DEF("port-security", [
                                                DEF("max-mac-count", [
                                                    DEF(NUMBER, required=True)
                                                ])
                                            ])
                                        ]),
                                    ])
                                ], multi=True)
                            ])
                        ], required=True, multi=True)
                    ]),
                    DEF("route", [
                        DEF("inet", [
                            DEF("static", [
                                DEF(IPv4_PREFIX, [
                                    DEF("next-hop", [
                                        DEF(IPv4_ADDRESS, multi=True)
                                    ])
                                ])
                            ])
                        ]),
                        DEF("inet6", [
                            DEF("static", [
                                DEF(IPv4_PREFIX, [
                                    DEF("next-hop", [
                                        DEF(IPv6_ADDRESS, multi=True)
                                    ])
                                ])
                            ])
                        ]),
                    ]),
                    DEF("protocols", [
                        DEF("spanning-tree", [
                            DEF("interface", [
                                DEF(IF_UNIT_NAME, [
                                    DEF("cost", [
                                        DEF(NUMBER, required=True)
                                    ])
                                ], multi=True)
                            ])
                        ])
                    ])
                ], required=True, multi=True)
            ], required=True)
        ], required=True, multi=True)
    ])
]
