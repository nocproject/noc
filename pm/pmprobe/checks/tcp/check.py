## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TCPCheck
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
## NOC modules
from noc.pm.pmprobe.checks.base import BaseCheck, Gauge
from noc.sa.interfaces.base import (StringParameter, IntParameter,
                                    REParameter, BooleanParameter)
from noc.pm.pmprobe.checks.tcpchecksocket import TCPCheckSocket


class TCPCheck(BaseCheck):
    name = "tcp"

    description = """
        TCP Check
    """

    default_port = None

    parameters = {
        "address": StringParameter(required=False),
        "port": IntParameter(required=False),
        "timeout": IntParameter(required=False, default=10),
        "request": StringParameter(required=False),
        "response": REParameter(required=False),
        "wait_close": BooleanParameter(default=False)
    }

    time_series = [
        # True or false, depending on result
        Gauge("result"),
        # TCP Three-way handshake delay (in seconds)
        Gauge("connect_delay"),
        # Delay between probe start
        # and beginning of receiving response
        # Only set for probes avaiting response
        Gauge("response_delay"),
        # Delay between probe
        #
        Gauge("response_time"),
        # Size of response (in octets).
        # Generated only when WAIT_UNTIL_CLOSE==True
        Gauge("response_size")
    ]

    form = "NOC.pm.check.tcp.TCPCheckForm"

    def __init__(self, *args, **kwargs):
        self.ready_event = threading.Event()
        self.result = {}
        super(TCPCheck, self).__init__(*args, **kwargs)

    def handle(self):
        self.ready_event.clear()
        self.result = {"result": False}
        TCPCheckSocket(
            check=self,
            address=self.config["address"],
            port=self.config["port"],
            timeout=self.config["timeout"],
            request=self.config.get("request"),
            match_response=self.config.get("response"),
            wait_close=self.config["wait_close"]
        )
        while not self.ready_event.is_set():
            self.ready_event.wait(1)
        return self.result

    def set_result(self, result):
        """
        Set result and signal check completion
        :param result:
        :return:
        """
        self.result.update(result)
        self.ready_event.set()
