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
        c = "DeviceInfo\n"
        v = self.http.get("/ISAPI/System/deviceInfo", cached=True, use_basic=True)
        v = v.replace("\n", "")
        root = ElementTree.fromstring(v)
        v = self.xml_2_dict(root)
        for key, value in sorted(six.iteritems(v["DeviceInfo"])):
            if key == "_text" or isinstance(value, six.string_types):
                continue
            c += "    %s %s\n" % (key, value[0]["_text"] if value[0] else "")
        v = self.http.get("/ISAPI/Streaming/channels", use_basic=True)
        v = v.replace("\n", "")
        root = ElementTree.fromstring(v)
        v = self.xml_2_dict(root)
        channels = v["StreamingChannelList"]["StreamingChannel"]
        for o in channels:
            c += "StreamingChannel %s\n" % o["id"][0]["_text"].strip("'")
            c += "  id %s\n" % o["id"][0]["_text"]
            c += '  channelName "%s"\n' % o["channelName"][0].get("_text", "")
            c += "  enabled %s\n" % o["enabled"][0]["_text"]
            video = o["Video"][0]
            c += "  Video\n"
            for key, value in sorted(six.iteritems(video)):
                if key == "_text" or isinstance(value, six.string_types):
                    continue
                c += "    %s %s\n" % (key, value[0]["_text"])
            if "Audio" in o:
                audio = o["Audio"][0]
                c += "  Audio\n"
                for key, value in sorted(six.iteritems(audio)):
                    if key == "_text" or isinstance(value, six.string_types):
                        continue
                    c += "    %s %s\n" % (key, value[0]["_text"])
        v = self.http.get("/ISAPI/Image/channels/1", use_basic=True)
        v = v.replace("\n", "")
        root = ElementTree.fromstring(v)
        v = self.xml_2_dict(root)
        o = v["ImageChannel"]

        color = o["Color"][0]
        c += "Color\n"
        for key, value in sorted(six.iteritems(color)):
            if key == "_text" or isinstance(value, six.string_types):
                continue
            c += "    %s %s\n" % (key, value[0]["_text"])
        if "WDR" in o:
            wdr = o["WDR"][0]
            c += "WDR\n"
            for key, value in sorted(six.iteritems(wdr)):
                if key == "_text" or isinstance(value, six.string_types):
                    continue
                c += "    %s %s\n" % (key, value[0]["_text"])
        blc = o["BLC"][0]
        c += "BLC\n"
        for key, value in sorted(six.iteritems(blc)):
            if key == "_text" or isinstance(value, six.string_types):
                continue
            try:
                c += "    %s %s\n" % (key, value[0]["_text"])
            except KeyError:
                continue
        try:
            v = self.http.get("/ISAPI/System/Video/inputs/channels", use_basic=True)
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            for vic in v["VideoInputChannelList"]["VideoInputChannel"]:
                # vid = vic["id"][0]["_text"]
                # for channelName overlay
                vname = vic["name"][0]["_text"]
            v = self.http.get("/ISAPI/System/Video/inputs/channels/1/overlays", use_basic=True)
            v = v.replace("\n", "")
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            c += "Overlay\n"
            for o in v["VideoOverlay"]:
                if o == "version" or o == "_text":
                    continue
                elif o == "TextOverlayList":
                    overlay = v["VideoOverlay"][o][0]
                    if overlay:
                        c += "  TextOverlay \n"
                    i = 1
                    if "_text" in overlay:
                        c += '    TextOverlay %d "%s"\n' % (i, overlay["_text"].strip())
                        continue
                    elif "TextOverlay" in overlay:
                        overlay = overlay["TextOverlay"]
                        for oo in overlay:
                            text = oo["displayText"][0]
                            if text:
                                c += '    TextOverlay %d "%s"\n' % (i, text["_text"])
                            else:
                                c += '    TextOverlay %d ""\n' % i
                            i = i + 1
                else:
                    c += "  %s\n" % o
                    for key, value in sorted(six.iteritems(v["VideoOverlay"][o][0])):
                        if key == "_text" or isinstance(value, six.string_types):
                            continue
                        c += "    %s %s\n" % (key, value[0]["_text"])
                if o == "channelNameOverlay":
                    c += "    %s %s\n" % ("channelName", vname)
        except HTTPError:
            pass
        try:
            v = self.http.get("/ISAPI/System/time", use_basic=True)
            v = v.replace("\n", "")
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            c += "Time\n"
            for key, value in sorted(six.iteritems(v["Time"])):
                if key == "_text" or isinstance(value, six.string_types) or key == "localTime":
                    continue
                c += "  %s %s\n" % (key, value[0]["_text"])
        except HTTPError:
            pass
        try:
            v = self.http.get("/ISAPI/System/time/ntpServers", use_basic=True)
            v = v.replace("\n", "")
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            ntp_servers = v["NTPServerList"]["NTPServer"]
            for i, o in enumerate(ntp_servers):
                aft = o["addressingFormatType"][0]["_text"]
                if aft == "hostname":
                    text = o["hostName"][0]["_text"]
                else:
                    text = o["ipAddress"][0]["_text"]
                c += "  NTPServer %d %s\n" % (i, text)
        except HTTPError:
            pass
        v = self.http.get("/ISAPI/Security/users", json=False, cached=True, use_basic=True)
        try:
            root = ElementTree.fromstring(v)
            v = self.xml_2_dict(root)
            c += "Users\n"
            for u in v["UserList"]["User"]:
                c += " user %s\n" % u["userName"][0]["_text"]
                for key, value in sorted(six.iteritems(u)):
                    if key == "_text" or isinstance(value, six.string_types):
                        continue
                    c += "    %s %s\n" % (key, value[0]["_text"])
        except ElementTree.ParseError:
            pass
        return c
