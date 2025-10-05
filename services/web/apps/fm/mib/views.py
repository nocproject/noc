# ---------------------------------------------------------------------
# fm.mib application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import networkx as nx

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.fm.models.mib import MIB
from noc.fm.models.mibdata import MIBData
from noc.fm.models.syntaxalias import SyntaxAlias
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.translation import ugettext as _


class MIBApplication(ExtDocApplication):
    """
    MIB application
    """

    title = _("MIB")
    menu = _("MIB")
    model = MIB

    @view(url="^(?P<id>[0-9a-f]{24})/data/$", method=["GET"], access="launch", api=True)
    def api_data(self, request, id):
        def insert_tree(data, ds):
            if len(data["path"]) + 1 == len(ds["path"]) and data["path"] == ds["path"][:-1]:
                # Direct child
                data["children"] = data.get("children", []) + [ds]
            else:
                if "children" not in data:
                    data["children"] = []
                # Descendant
                for c in data["children"]:
                    if c["path"] == ds["path"][: len(c["path"])]:
                        insert_tree(c, ds)
                        return
                cp = ds["path"][: -(len(data["path"]) + 1)]
                c = {"oid": ".".join(str(x) for x in cp), "path": cp, "children": []}
                data["children"] += [c]
                insert_tree(c, ds)

        def fix_tree(data):
            if "path" in data:
                del data["path"]
            if "children" in data:
                if "leaf" in data:
                    del data["leaf"]
                data["children"] = sorted(data["children"], key=lambda x: x["path"])
                data["expanded"] = True
                for c in data["children"]:
                    fix_tree(c)

        def oid_to_list(oid):
            return [int(x) for x in oid.split(".")]

        def list_to_oid(li):
            return ".".join(str(x) for x in li)

        def find_start_node(s):
            path = oid_to_list(s.pop())
            if len(s) == 0:
                return path
            for i in s:
                pathi = oid_to_list(i)
                if len(path) > len(pathi):
                    path = pathi
                elif len(path) == len(pathi):
                    path = pathi if path[-1] > pathi[-1] else path
            return path

        def find_root_node(g):
            root = None
            for n in g.nodes(data=True):
                if root is None or len(root[1]["ds"]["path"]) > len(n[1]["ds"]["path"]):
                    root = n
            return root[0]

        G = nx.DiGraph()
        mib = self.get_object_or_404(MIB, id=id)
        data = {"oid": "", "leaf": True, "path": []}
        for d in MIBData.objects.filter(mib=mib.id).order_by("oid"):
            ds = {
                "oid": d.oid,
                "name": d.name,
                "path": oid_to_list(d.oid),
                "leaf": True,
                "description": d.description,
                "syntax": self.get_syntax(d),
            }
            G.add_node(ds["oid"], ds=ds)
        for child in G.nodes(data=True):
            for parent in G.nodes(data=True):
                if (
                    child[1]["ds"]["oid"] != parent[1]["ds"]["oid"]
                    and parent[1]["ds"]["path"] == child[1]["ds"]["path"][:-1]
                ):
                    G.add_edge(parent[0], child[0])
        while sum(1 for x in nx.connected_components(G.to_undirected())) != 1:
            for g in nx.connected_components(G.to_undirected()):
                start_node = find_start_node(g)
                oid_new_node = list_to_oid(start_node[:-1])
                path_new_node = start_node[:-1]
                G.add_node(
                    oid_new_node,
                    ds={
                        "oid": oid_new_node,
                        "name": "",
                        "path": path_new_node,
                        "leaf": False,
                        "decription": "",
                    },
                )
                G.add_edge(oid_new_node, list_to_oid(start_node))
                for parent in G.nodes(data=True):
                    if (
                        oid_new_node != parent[1]["ds"]["oid"]
                        and parent[1]["ds"]["path"] == path_new_node[:-1]
                    ):
                        G.add_edge(parent[0], oid_new_node)
        for a in nx.dfs_tree(G, find_root_node(G)):
            insert_tree(data, nx.get_node_attributes(G, "ds")[a])
        fix_tree(data)
        return data

    def get_syntax(self, x):
        def syntax_descr(syntax):
            if not syntax:
                return []
            s = []
            s += [syntax["base_type"]]
            if "display_hint" in syntax:
                s += ["display-hint: %s" % syntax["display_hint"]]
            if syntax["base_type"] in ("Enumeration", "Bits") and "enum_map" in syntax:
                # Display enumeration
                for k in sorted(syntax["enum_map"], key=lambda x: int(x)):
                    s += ["%s -> %s" % (k, syntax["enum_map"][k])]
            return s

        s = []
        sa = SyntaxAlias.rewrite(x.name, x.syntax)
        if x.syntax:
            s += syntax_descr(x.syntax)
        if sa != x.syntax:
            s += ["", "Effective syntax:"]
            s += syntax_descr(sa)
        return "\n".join(s)

    @view(url="^upload/", method=["POST"], access="create", api=True)
    def api_upload(self, request):
        left = {}  # name -> data
        for f in request.FILES:
            left[f] = request.FILES[f]
        errors = {}
        while left:
            n = len(left)
            for name in list(left.keys()):
                try:
                    svc = open_sync_rpc("mib")
                    r = svc.compile(MIB.guess_encoding(left[name].read()))
                    if r.get("status"):
                        del left[name]
                        if name in errors:
                            del errors[name]
                    else:
                        errors[name] = r["msg"]
                except RPCError as e:
                    errors[name] = str(e)
            if len(left) == n:
                # Failed to upload anything, stopping
                break
        return self.render_json(
            {"success": len(left) == 0, "message": f"ERROR: {errors}"}, status=self.OK
        )

    @view(url="^(?P<id>[0-9a-f]{24})/text/$", method=["GET"], access="launch", api=True)
    def api_text(self, request, id):
        mib = self.get_object_or_404(MIB, id=id)
        try:
            svc = open_sync_rpc("mib")
            r = svc.get_text(mib.name)
            if r.get("status"):
                return r["data"]
        except RPCError:
            pass
        return ""
