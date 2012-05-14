# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.reportoverview
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.reportapplication import ReportApplication
from noc.main.models import CustomField
from noc.ip.models import VRFGroup, VRF, Prefix, IP
from noc.lib.ip import IP
from noc.settings import ADMIN_MEDIA_PREFIX

prefix_fields = [f for f in CustomField.table_fields("ip_prefix")
                 if not f.is_hidden]

CSS = """
<style>
TABLE TR TD {
    border: none;
}

.block {
    margin: 4px;
    background-color: #c0c0c0;
    color: #000000;
    border-radius: 8px;
    padding: 8px;
    border: 1px solid #808080;
}
</style>
"""

class Node(object):
    def __init__(self):
        self.children = []
        self.height = 0
        self.depth = 0
        self.populate()
        self.get_depth()
        self.get_height()

    def get_depth(self):
        if not self.depth:
            if self.children:
                self.depth = 1 + max(c.get_depth()
                    for c in self.children)
            else:
                self.depth = 1
        return self.depth

    def get_height(self):
        if not self.height:
            if self.children:
                self.height = sum(c.get_height() for c in self.children)
            else:
                self.height = 1
        return self.height

    def populate(self):
        pass

    def update_report(self, r, current_level, max_level):
        if self.height > 1:
            r += ["<td rowspan='%s' class='block'>" % self.height]
        else:
            r += ["<td class='block'>"]
        r += [self.get_html(), "</td>"]
        if self.children:
            for c in self.children:
                c.update_report(r, current_level + 1, max_level)
        else:
            if current_level < max_level:
                # Fill empty cells to the end
                r += ["<td></td>"] * (max_level - current_level)
            r += ["</tr><tr>"]

    def get_html(self):
        return ""


class VRFGroupNode(Node):
    def __init__(self, vrf_group):
        self.vrf_group = vrf_group
        super(VRFGroupNode, self).__init__()

    def get_html(self):
        return "<b>VRF Group: %s</b>" % self.vrf_group.name


class VRFNode(Node):
    def __init__(self, vrf):
        self.vrf = vrf
        super(VRFNode, self).__init__()

    def populate(self):
        root = Prefix.objects.get(vrf=self.vrf, prefix="0.0.0.0/0")
        for p in root.children_set.order_by("prefix"):
            self.children += [PrefixNode(p)]

    def get_html(self):
        return "<b>VRF %s</b><br/>RD: %s" % (self.vrf.name, self.vrf.rd)


class PrefixNode(Node):
    def __init__(self, prefix):
        self.prefix = prefix
        if self.prefix.afi == "4":
            self.size = 2 ** (32 - int(self.prefix.prefix.split("/")[1]))
        else:
            self.size = 0
        self.used = None
        super(PrefixNode, self).__init__()
        self.update_usage()

    def populate(self):
        for p in self.prefix.children_set.order_by("prefix"):
            self.children += [PrefixNode(p)]

    def get_html(self):
        r = ["<b><u>%s</u></b>" % self.prefix.prefix]
        if self.prefix.description:
            r += ["<br/>%s" % self.prefix.description]
        if self.used is not None:
            r += ["<br/><b>%s</b>" % self.used]
        # Show custom fields
        for f in prefix_fields:
            v = getattr(self.prefix, f.name)
            if v is None or v == "":
                continue
            if f.type == "bool":
                t = "yes" if f else "no"
                icon = "<img src='%simg/admin/icon-%s.gif' />" % (
                    ADMIN_MEDIA_PREFIX, t)
                r += ["<br/>%s: %s" % (f.label, icon)]
            else:
                r += ["<br/>%s: %s" % (f.label, v)]
        return "".join(r)

    def update_usage(self):
        if self.prefix.afi != "4":
            return
        p = IP.prefix(self.prefix.prefix)
        ps = p.size
        if ps < 2:
            return
        if self.children:
            # Count prefixes
            u = sum(c.size for c in self.children)
            pu = min(int(float(u) * 100 / float(ps)), 100)
        else:
            # Count addresses
            u = self.prefix.address_set.count()
            if ps > 2:
                pu = int(float(u) * 100 / float(ps - 2))
            else:
                pu = int(float(u) * 100 / float(ps))
        self.used = "Usage: %s%%" % pu


class ReportOverviewApplication(ReportApplication):
    title = "Overview"

    def report_html(self):
        # Prepare tree
        nodes = []
        for vrf_group in VRFGroup.objects.order_by("name"):
            if vrf_group.address_constraint == "G":
                nodes += [VRFGroupNode(vrf_group)]
            else:
                for vrf in vrf_group.vrf_set.order_by("name"):
                    nodes += [VRFNode(vrf)]
        # Render tree
        max_level = max(n.get_depth() for n in nodes)
        r = [CSS, "<table border='0'>"]
        r += ["<tr>"]
        for n in nodes:
            n.update_report(r, 1, max_level)
        r += ["</tr>"]
        r += ["</table>"]
        return "".join(r)
