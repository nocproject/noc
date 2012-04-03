# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetDOMStatus interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetDOMStatus(Interface):
    """
    Get Digital Optical Monitoring status

    >>> IGetDOMStatus().clean_result([{"interface": "Gi 0/1",\
                                       "optical_tx_dbm": "-2.5",\
                                       "optical_rx_dbm": None}])
    [{'interface': 'Gi 0/1', 'optical_rx_dbm': None, 'optical_tx_dbm': -2.5}]
    """
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
        "temp_c": (FloatParameter(required=False) |
                   NoneParameter(required=False)),
        "voltage_v": (FloatParameter(required=False) |
                      NoneParameter(required=False)),
        "current_ma": (FloatParameter(required=False) |
                       NoneParameter(required=False)),
        "optical_rx_dbm": (FloatParameter(required=False) |
                           NoneParameter(required=False)),
        "optical_tx_dbm": (FloatParameter(required=False) |
                           NoneParameter(required=False)),
        }))
    template = "interfaces/igetdomstatus.html"
