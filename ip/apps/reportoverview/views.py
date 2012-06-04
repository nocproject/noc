# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.reportoverview
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import connection
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
    def __init__(self, app):
        self.app = app
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
    def __init__(self, app, vrf_group):
        self.vrf_group = vrf_group
        self.vrfs = list(vrf_group.vrf_set.all())
        super(VRFGroupNode, self).__init__(app)

    def populate(self):
        if self.vrfs:
            vid = "{%s}" % ",".join([str(v.id) for v in self.vrfs ])
            root = Prefix.objects.get(vrf=self.vrfs[0],
                prefix="0.0.0.0/0")
            c = GPrefixNode(self.app, root, vid)
            self.children = c.children  # Relink

    def get_html(self):
        r = ["<b>VRF Group: %s</b>" % self.vrf_group.name]
        r += ["&nbsp;&nbsp;<b>%s</b> (RD: %s)" % (v.name, v.rd)
              for v in self.vrfs]
        return "<br>".join(r)


class VRFNode(Node):
    def __init__(self, app, vrf):
        self.vrf = vrf
        super(VRFNode, self).__init__(app)

    def populate(self):
        root = Prefix.objects.get(vrf=self.vrf, prefix="0.0.0.0/0")
        for p in root.children_set.order_by("prefix"):
            self.children += [PrefixNode(self.app, p)]

    def get_html(self):
        return "<b>VRF %s</b><br/>RD: %s" % (self.vrf.name, self.vrf.rd)


class PrefixNode(Node):
    show_vrf = False
    def __init__(self, app, prefix):
        self.prefix = prefix
        if self.prefix.afi == "4":
            self.size = 2 ** (32 - int(self.prefix.prefix.split("/")[1]))
        else:
            self.size = 0
        self.used = None
        super(PrefixNode, self).__init__(app)
        self.update_usage()

    def __unicode__(self):
        return self.prefix

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.prefix)

    def populate(self):
        for p in self.prefix.children_set.order_by("prefix"):
            self.children += [PrefixNode(self.app, p)]

    def get_html(self):
        r = ["<b><u>%s</u></b>" % self.prefix.prefix]
        if self.prefix.description:
            r += ["<br/>%s" % self.prefix.description]
        if self.show_vrf:
            r += ["<br/>VRF: %s" % self.prefix.vrf.name]
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
            u = self.app.ip_usage.get(self.prefix.id, 0)
            if ps > 2:
                pu = int(float(u) * 100 / float(ps - 2))
            else:
                pu = int(float(u) * 100 / float(ps))
        self.used = "Usage: %s%%" % pu


class GPrefixNode(PrefixNode):
    show_vrf = True
    def __init__(self, app, prefix, vrfs):
        self.vrfs = vrfs
        super(GPrefixNode, self).__init__(app, prefix)

    def populate(self):
        self.children = [
            GPrefixNode(self.app, p, self.vrfs) for p in
            Prefix.objects.raw("""
                SELECT id FROM ip_prefix p
                WHERE
                        vrf_id = ANY (%s::integer[])
                    AND prefix << %s
                    AND NOT EXISTS (
                        SELECT id
                        FROM ip_prefix
                        WHERE
                            vrf_id = ANY (%s::integer[])
                            AND prefix << %s
                            AND prefix >> p.prefix
                        )
                ORDER BY p.prefix
            """, [self.vrfs, self.prefix.prefix,
                  self.vrfs, self.prefix.prefix])]


class ReportOverviewApplication(ReportApplication):
    title = "Overview"

    def get_ip_usage(self):
        """
        Returns dict of prefix_id -> ip address count
        :return:
        """
        c = connection.cursor()
        c.execute("""
            SELECT prefix_id, COUNT(*)
            FROM ip_address
            GROUP BY 1
            """)
        return dict(c.fetchall())

    def report_html(self):
        #
        self.ip_usage = self.get_ip_usage()
        # Prepare tree
        nodes = []
        for vrf_group in VRFGroup.objects.order_by("name"):
            if vrf_group.address_constraint == "G":
                nodes += [VRFGroupNode(self, vrf_group)]
            else:
                for vrf in vrf_group.vrf_set.order_by("name"):
                    nodes += [VRFNode(self, vrf)]
        # Render tree
        max_level = max(n.get_depth() for n in nodes)
        r = [CSS, "<table border='0'>"]
        r += ["<tr>"]
        for n in nodes:
            n.update_report(r, 1, max_level)
        r += ["</tr>"]
        r += ["</table>"]
        return "".join(r)
