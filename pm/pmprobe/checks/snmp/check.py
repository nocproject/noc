## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMPCheck
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
## NOC modules
from noc.pm.pmprobe.checks.base import BaseCheck, Counter, Gauge
from noc.sa.interfaces.base import (StringParameter, IntParameter,
                                    OIDParameter)
from noc.pm.pmprobe.checks.snmpgetsocket import SNMPGetSocket


class SNMPCheck(BaseCheck):
    name = "snmp"

    description = """
        SNMP Get check
    """

    parameters = {
        "address": StringParameter(required=False),
        "port": IntParameter(required=False, default=161),
        "community": StringParameter(required=False),
        "oid": StringParameter(required=False),
        "timeout": IntParameter(required=False, default=10)
    }

    time_series = [
        Gauge("value")
    ]

    form = "NOC.pm.check.snmp.SNMPCheckForm"

    def __init__(self, *args, **kwargs):
        self.ready_event = threading.Event()
        self.result = {}
        super(SNMPCheck, self).__init__(*args, **kwargs)

    def handle(self):
        self.ready_event.clear()
        self.result = {"result": False}
        s = SNMPGetSocket(
            check=self,
            address=self.config.get("address"),
            port=self.config.get("port"),
            timeout=self.config.get("timeout")
        )
        s.create_socket()
        s.get_request(
            community=self.config["community"],
            oids=[self.config["oid"]]
        )
        while not self.ready_event.is_set():
            self.ready_event.wait(1)
        return {"value": self.result.get(self.config.get("oid"))}

    def set_result(self, result):
        """
        Set result and signal check completion
        :param result:
        :return:
        """
        self.info("Set result: %s" % result)
        self.result.update(result)
        self.ready_event.set()
