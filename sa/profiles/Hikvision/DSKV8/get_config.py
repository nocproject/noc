# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Hikvision.DSKV8.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import xml.etree.ElementTree as ElementTree
from copy import copy
import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig
from noc.core.script.http.base import HTTPError


class Script(BaseScript):
    name = "Hikvision.DSKV8.get_config"
    cache = True
    interface = IGetConfig

    def xml_2_dict(self, r, root=True):
        if root:
            t = r.tag.split("}")[1][0:]
            return {t: self.xml_2_dict(r, False)}
        d = copy(r.attrib)
        if r.text:
            d["_text"] = r.text
        for x in r.findall("./*"):
            t = x.tag.split("}")[1][0:]
            if t not in d:
                d[t] = []
            d[t].append(self.xml_2_dict(x, False))
        return d

    def execute(self, **kwargs):
        c = ""
        v = self.http.get("/ISAPI/Streaming/channels", use_basic=True)
        v = v.replace("\n", "")
        root = ElementTree.fromstring(v)
        v = self.xml_2_dict(root)
        channels = v["StreamingChannelList"]["StreamingChannel"]
        i = 1
        for o in channels:
            c += "StreamingChannel:\n"
            c += "    id: %s\n" % o["id"][0]["_text"]
            c += '    channelName: "%s"\n' % o["channelName"][0]["_text"]
            c += "    enabled: %s\n" % o["enabled"][0]["_text"]
            video = o["Video"][0]
            c += "Video:\n"
            for key, value in sorted(six.iteritems(video)):
                if key == "_text" or isinstance(value, six.string_types):
                    continue
                c += "    %s: %s\n" % (key, value[0]["_text"])
        v = self.http.get("/ISAPI/Image/channels/1/color", use_basic=True)
        v = v.replace("\n", "")
        root = ElementTree.fromstring(v)
        v = self.xml_2_dict(root)
        color = v["Color"]
        c += "Color:\n"
        for key, value in sorted(six.iteritems(color)):
            if key == "_text" or isinstance(value, six.string_types):
                continue
            c += "    %s: %s\n" % (key, value[0]["_text"])

        try:
            v = self.http.get("/ISAPI/Image/channels/1/WDR", use_basic=True)
            v = v.replace("\n", "")
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            c += "WDR:\n"
            c += "    mode: %s\n" % v["WDR"]["mode"][0]["_text"]
            c += "    WDRLevel: %s\n" % v["WDR"]["WDRLevel"][0]["_text"]
        except HTTPError:
            pass

        try:
            v = self.http.get("/ISAPI/Image/channels/1/BLC", use_basic=True)
            v = v.replace("\n", "")
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            c += "BLC:\n"
            c += "    enabled: %s\n" % v["BLC"]["enabled"][0]["_text"]
            if "BLCMode" in v["BLC"]:
                c += "    BLCMode: %s\n" % v["BLC"]["BLCMode"][0]["_text"]
        except HTTPError:
            pass

        try:
            v = self.http.get(
                "/ISAPI/System/Video/inputs/channels/1/overlays/capabilities", use_basic=True
            )
            v = v.replace("\n", "")
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            overlay = v["VideoOverlay"]["TextOverlayList"][0]
            if "TextOverlay" in overlay:
                overlay = overlay["TextOverlay"]
                if overlay:
                    c += "Overlays:\n"
                i = 1
                for o in overlay:
                    text = o["displayText"][0]
                    if text:
                        c += '    TextOverlay%d: "%s"\n' % (i, text["_text"])
                    else:
                        c += '    TextOverlay%d: ""\n' % i
                    i = i + 1
        except HTTPError:
            pass

        try:
            v = self.http.get("/ISAPI/System/time", use_basic=True)
            v = v.replace("\n", "")
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            timeMode = v["Time"]["timeMode"][0]["_text"]
            c += "Time:\n"
            c += "    timeMode: %s\n" % timeMode
        except HTTPError:
            pass

        try:
            v = self.http.get("/ISAPI/System/time/ntpServers", use_basic=True)
            v = v.replace("\n", "")
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            ntp_servers = v["NTPServerList"]["NTPServer"]
            if ntp_servers:
                c += "NTP:\n"
            i = 1
            for o in ntp_servers:
                text = o["ipAddress"][0]["_text"]
                c += "    NTPServer%d: %s\n" % (i, text)
        except HTTPError:
            pass

        return c
