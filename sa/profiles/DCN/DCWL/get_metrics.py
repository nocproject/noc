# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# DCN.DCWL.get_metrics
#----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
#----------------------------------------------------------------------

# Python modules
from __future__ import division
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript

class Script(GetMetricsScript):
    name = "DCN.DCWL.get_metrics"

    ALL_METRICS = set(["Radio | TxPower", "Interface | Load | In", "Interface | Load | Out", "Interface | Packets | In",
                       "Interface | Packets | OUT", "Interface | Errors | In", "Interface | Errors | Out",
                       "Radio | Channel | Util", "Radio | Channel | Free", "Radio | Channel | Busy",
                       "Radio | Channel | TxFrame", "Radio | Channel | RxFrame"])

    TYPE = {
        "Radio | TxPower": "gauge",
        "Interface | Load | In": "counter",
        "Interface | Load | Out": "counter",
        "Radio | Channel | Util": "gauge",
        "Radio | Channel | Free": "gauge",
        "Radio | Channel | Busy": "gauge",
        "Radio | Channel | TxFrame": "gauge",
        "Radio | Channel | RxFrame": "gauge",
        "Interface | Packets | In": "counter",
        "Interface | Packets | Out": "counter",
        "Interface | Errors | In": "counter",
        "Interface | Errors | Out": "counter"
    }

    @classmethod
    def get_metric_type(cls, name):
         c = cls.TYPE.get(name)
         return c

    def collect_profile_metrics(self, metrics):
        self.logger.debug("Merics %s" % metrics)
        if self.ALL_METRICS.intersection(set(m.metric for m in metrics)):
            # check
            self.collect_cli_metrics(metrics)

    def collect_cli_metrics(self, metrics):
        ts = self.get_ts()
        m = self.get_cli_metrics()
        for bv in metrics:
            if bv.metric in self.ALL_METRICS:
                id = tuple(bv.path + [bv.metric])
                if id in m:
                    self.set_metric(
                        id=bv.id,
                        metric=bv.metric,
                        value=m[id],
                        type=self.get_metric_type(bv.metric),
                        ts=ts,
                        path=bv.path,
                    )

    def get_cli_metrics(self):
        res = {}
        wres = {}
        name = None
        ssid = None
        w = self.cli("get radio all detail")
        for wline in w.splitlines():
            wr = wline.split(" ", 1)
            if wr[0] == "name":
                wname = wr[1].strip()
            elif wr[0] == "tx-power":
                txpower = ((27 / 100) * int(wr[1].strip()))  # Max TxPower 27dBm, convert % -> dBm
            elif wr[0] == "channel-util":
                channelutil = wr[1].strip()
            elif wr[0] == "channel-free":
                channelfree = wr[1].strip()
            elif wr[0] == "channel-busy":
                channelbusy = wr[1].strip()
            elif wr[0] == "channel-tx-frame":
                channeltxframe = wr[1].strip()
            elif wr[0] == "channel-rx-frame":
                channelrxframe = wr[1].strip()
                wres[wname] = {"txpower": txpower, "channelutil": channelutil, "channelfree": channelfree, "channelbusy": channelbusy, "channeltxframe": channeltxframe, "channelrxframe": channelrxframe}
        c = self.cli("get interface all detail")
        for vline in c.splitlines():
            rr = vline.split(' ', 1)
            if rr[0] == "name":
                name = rr[1].strip()
            elif rr[0] == "rx-bytes":
                rxbytes = rr[1].strip()
            elif rr[0] == "rx-packets":
                rxpackets = rr[1].strip()
            elif rr[0] == "rx-errors":
                rxerrors = rr[1].strip()
            elif rr[0] == "tx-bytes":
                txbytes = rr[1].strip()
            elif rr[0] == "tx-packets":
                txpackets = rr[1].strip()
            elif rr[0] == "tx-errors":
                txerrors = rr[1].strip()
                res[name] = {"rxbytes": rxbytes, "rxpackets": rxpackets, "rxerrors": rxerrors, "txbytes": txbytes, "txpackets": txpackets, "txerrors": txerrors}
            elif rr[0] == "ssid":
                ssid = rr[1].strip().replace(" ", "").replace("Managed", "")
            elif rr[0] == "bss":
                bss = rr[1].strip()
            if ssid:
                res[name] = {"rxbytes": rxbytes, "rxpackets": rxpackets, "rxerrors": rxerrors, "txbytes": txbytes, "txpackets": txpackets, "txerrors": txerrors, "iface": "%s.%s" % (name, ssid), "bss": bss}
        for s in res.items():
            if not "bss" in s[1]:
                continue
            v = self.cli("get bss %s detail" % s[1]["bss"])
            for vline in v.splitlines():
                rr = vline.split(' ', 1)
                if rr[0] == "status":
                    status = rr[1].strip()
                elif rr[0] == "radio":
                    radio = rr[1].strip()
                elif rr[0] == "beacon-interface":
                    name = rr[1].strip()
                    if name in res.keys():
                        res[name].update({"radio": radio, "status": status})
        r = {}
        for o in res.items():
            if "status" in o[1]:
                if o[1]["status"] == "down":
                    continue
                wiface = o[1]["iface"]
                iface = o[0]
                for w in wres.items():
                    if w[0] in o[1]["radio"]:
                        txpower = w[1]["txpower"]
                        cu = w[1]["channelutil"]
                        cf = w[1]["channelfree"]
                        cb = w[1]["channelbusy"]
                        ctf = w[1]["channeltxframe"]
                        crf = w[1]["channelrxframe"]
                        txbytes = o[1]["txbytes"]
                        rxbytes = o[1]["rxbytes"]
                        rxpackets = o[1]["rxpackets"]
                        txpackets = o[1]["txpackets"]
                        rxerrors = o[1]["rxerrors"]
                        txerrors = o[1]["txerrors"]
                        r[("", "", "", wiface, "Radio | TxPower")] = txpower
                        r[("", "", "", wiface, "Radio | Channel | Util")] = cu
                        r[("", "", "", wiface, "Radio | Channel | Free")] = cf
                        r[("", "", "", wiface, "Radio | Channel | Busy")] = cb
                        r[("", "", "", wiface, "Radio | Channel | TxFrame")] = ctf
                        r[("", "", "", wiface, "Radio | Channel | RxFrame")] = crf
                        r[("", "", "", wiface, "Interface | Load | In")] = rxbytes
                        r[("", "", "", wiface, "Interface | Load | Out")] = txbytes
                        r[("", "", "", wiface, "Interface | Packets | In")] = rxpackets
                        r[("", "", "", wiface, "Interface | Packets | Out")] = txpackets
                        r[("", "", "", wiface, "Interface | Errors | In")] = rxerrors
                        r[("", "", "", wiface, "Interface | Errors | Out")] = txerrors
                        r[("", "", "", iface, "Interface | Load | In")] = rxbytes
                        r[("", "", "", iface, "Interface | Load | Out")] = txbytes
                        r[("", "", "", iface, "Interface | Packets | In")] = rxpackets
                        r[("", "", "", iface, "Interface | Packets | Out")] = txpackets
                        r[("", "", "", iface, "Interface | Errors | In")] = rxerrors
                        r[("", "", "", iface, "Interface | Errors | Out")] = txerrors
            else:
                iface = o[0]
                rxbytes = o[1]["rxbytes"]
                txbytes = o[1]["txbytes"]
                rxpackets = o[1]["rxpackets"]
                txpackets = o[1]["txpackets"]
                rxerrors = o[1]["rxerrors"]
                txerrors = o[1]["txerrors"]
                r[("", "", "", iface, "Interface | Load | In")] = rxbytes
                r[("", "", "", iface, "Interface | Load | Out")] = txbytes
                r[("", "", "", iface, "Interface | Packets | In")] = rxpackets
                r[("", "", "", iface, "Interface | Packets | Out")] = txpackets
                r[("", "", "", iface, "Interface | Errors | In")] = rxerrors
                r[("", "", "", iface, "Interface | Errors | Out")] = txerrors
        return r