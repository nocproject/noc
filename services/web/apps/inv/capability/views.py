# ---------------------------------------------------------------------
# inv.capability application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import itertools
from collections import defaultdict

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.inv.models.capability import Capability
from noc.main.models.doccategory import DocCategory
from noc.core.translation import ugettext as _


class CapabilityApplication(ExtDocApplication):
    """
    Capability application
    """

    title = _("Capability")
    menu = [_("Setup"), _("Capabilities")]
    model = Capability
    query_fields = ["name", "description"]
    query_condition = "icontains"
    parent_model = DocCategory
    parent_field = "parent"

    @view(method=["GET"], url="^tree$", access="read", api=True)
    def get_tree(self, request):
        """
        Return capabilities for tree build.
        root: {
        expanded: true,
        children: [
            { text: 'detention', leaf: true },
            { text: 'homework', expanded: true, children: [
                { text: 'book report', leaf: true },
                { text: 'algebra', leaf: true}
            ] },
            { text: 'buy lottery tickets', leaf: true }
        ]
        }
        :param request:
        :return:
        """
        root_c = {"text": "root", "children": []}

        caps_s = sorted(
            Capability.objects.filter().only("id", "name", "type"),
            key=lambda x: (x.name.split("|")[0], x.name.count("|"), x.name),
        )
        caps_d = {
            tuple(k): list(g)
            for (k, g) in itertools.groupby(caps_s, key=lambda x: x.name.split("|")[:-1])
        }

        context = defaultdict(list)
        for e in caps_d:
            children = [
                {
                    "text": f.name.split()[-1].strip(),
                    "type": f.type.value,
                    "id": str(f.id),
                    "leaf": True,
                    "checked": False,
                }
                for f in caps_d[e]
            ]
            if not e:
                self.logger.warning("Not e: %s, children: %s" % (caps_d[e], children))
                # @todo Update inside list
                context[children[0]["text"]] += children
            for b in reversed(e):
                context[b.strip()] += children
                children = [{"text": b.strip(), "children": context[b.strip()]}]
        kk = {k[0].strip() for (k, g) in itertools.groupby(caps_d, key=lambda x: x[:1]) if k}
        for k in kk:
            root_c["children"] += [{"text": k, "children": context[k]}]

        return self.render_json(root_c)
