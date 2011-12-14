# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetCopperTDRDiag interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetCopperTDRDiag(Interface):
    """
    Get copper cable TDR diagnostic results

    >>> IGetCopperTDRDiag().clean_result([\
        {\
            "interface": "Gi 0/1",\
            "pairs": [\
                {"pair": 1, "status": "T", "distance_cm": 600},\
                {"pair": 2, "status": "T", "distance_cm": 600},\
                {"pair": 3, "status": "T", "distance_cm": 600},\
                {"pair": 4, "status": "T", "distance_cm": 600}\
            ]\
        },\
        {\
            "interface": "Gi 0/2",\
            "pairs": [\
                {"pair": 1, "status": "T",\
                    "distance_cm": 600, "variance_cm": 200},\
                {"pair": 2, "status": "S",\
                    "distance_cm": 300, "variance_cm": "200"},\
                {"pair": 3, "status": "O", "distance_cm": 0},\
                {"pair": 4, "status": "O", "distance_cm": 0}\
            ]\
        }\
    ])
    [{'interface': 'Gi 0/1',\
        'pairs': [{'pair': 1, 'status': 'T', 'distance_cm': 600},\
                 {'pair': 2, 'status': 'T', 'distance_cm': 600},\
                 {'pair': 3, 'status': 'T', 'distance_cm': 600},\
                 {'pair': 4, 'status': 'T', 'distance_cm': 600}]},\
     {'interface': 'Gi 0/2',\
        'pairs': [{'pair': 1, 'status': 'T',\
                    'distance_cm': 600, 'variance_cm': 200},\
                 {'pair': 2, 'status': 'S',\
                    'distance_cm': 300, 'variance_cm': 200},\
                 {'pair': 3, 'status': 'O', 'distance_cm': 0},\
                 {'pair': 4, 'status': 'O', 'distance_cm': 0}]}]
    """
    interface = InterfaceNameParameter(required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "interface": InterfaceNameParameter(),
        "pairs": ListOfParameter(element=DictParameter(attrs={
            "pair": IntParameter(),
            "status": StringParameter(choices=[
                "T",  # Terminated
                "O",  # Open
                "S",  # Short
                "N"   # N/A
            ]),
            # Measured distance in centimeters.
            # Interpretation depends on status.
            # T - cable length
            # O - always 0
            # S - distance to short-circuit
            # N - always 0
            "distance_cm": IntParameter(),
            # Optional measurement variance
            "variance_cm": IntParameter(required=False)
        }))
    }))
