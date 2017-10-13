# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetDOMStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, InterfaceNameParameter,
                  DictParameter, FloatParameter, NoneParameter)


class IGetDOMStatus(BaseInterface):
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
        "temp_c": (NoneParameter(required=False) |
                   FloatParameter(required=False)),
        "voltage_v": (NoneParameter(required=False) |
                      FloatParameter(required=False)),
        "current_ma": (NoneParameter(required=False) |
                       FloatParameter(required=False)),
        "optical_rx_dbm": (NoneParameter(required=False) |
                           FloatParameter(required=False)),
        "optical_tx_dbm": (NoneParameter(required=False) |
                           FloatParameter(required=False)),
        }))
    preview = "NOC.sa.managedobject.scripts.ShowDomStatus"
