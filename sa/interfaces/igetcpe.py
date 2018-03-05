# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetCPE - interface to query ARP cache
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (StringParameter, InterfaceNameParameter,
                  IPv4Parameter, MACAddressParameter, DictListParameter,
                  FloatParameter)


class IGetCPE(BaseInterface):
    """
    * id - local CPE id (used for management commands)
    * global_id -- global CPE id, used for inter-controller movement tracking
    * name -- symbolic CPE name
    * status -- CPE status
        * active -- cpe is active (default)
        * inactive -- cpe is inactive (but remembered)
        * approval -- waiting for approval
        * firmware -- upgrading firmware
        * provisioning -- provisioning
        * other -- other status
    * type - CPE type
        * ap - WiFi AP
        * bs - Base Station
        * st - Sector from Base Station
        * dsl - DSL modem
        * ont - PON ONT
        * docsis - DOCSIS cable modem
        * other - all other typesu8
    * interface - controller's physical interface leading to CPE
    * model - CPE model
    * serial - CPE serial number
    * ip - CPE IP
    * mac - CPE mac
    * modulation - Modulation used
    * description - CPE description string
    * location - CPE location string
    * distance - Calculated distance in meters
    """
    returns = DictListParameter(attrs={
        "id": StringParameter(),
        "global_id": StringParameter(),
        "name": StringParameter(required=False),
        "status": StringParameter(choices=[
            "active",
            "inactive",
            "approval",
            "firmware",
            "provisioning",
            "other"
        ], default="active"),
        "type": StringParameter(choices=[
            "ap",
            "bs",
            "st",
            "dsl",
            "ont",
            "docsis",
            "other"
        ]),
        "interface": InterfaceNameParameter(required=False),
        "model": StringParameter(required=False),
        "serial": StringParameter(required=False),
        "ip": IPv4Parameter(required=False),
        "mac": MACAddressParameter(required=False),
        "modulation": StringParameter(required=False),
        "description": StringParameter(required=False),
        "location": StringParameter(required=False),
        "distance": FloatParameter(required=False)
    })
