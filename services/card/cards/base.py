# ---------------------------------------------------------------------
# Base card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import datetime
import operator

# Third-party modules
from jinja2 import Template, Environment
from typing import Dict, Any

# NOC modules
from noc.core.translation import ugettext as _
from noc.sa.models.useraccess import UserAccess
from noc.config import config
from noc.core.perf import metrics


class BaseCard(object):
    name = None
    default_template_name = "default"
    template_cache = {}  # name -> Template instance
    actions = []
    TEMPLATE_PATH = config.get_customized_paths(
        os.path.join("services", "card", "templates"), prefer_custom=True
    )
    model = None
    DEFAULT_MO_TITLE_TEMPLATE = "{{ object.object_profile.name }}: {{ object.name }}"
    DEFAULT_SERVICE_TITLE_TEMPLATE = (
        "{% if object.profile.glyph %}<i class='{{ object.profile.glyph }}'></i> "
    )
    DEFAULT_SERVICE_TITLE_TEMPLATE += "{%endif %}{{ object.profile.name }}: {{ object.order_id }}"
    # Card javascript
    card_js = []
    card_css = []

    class RedirectError(Exception):
        pass

    class NotFoundError(Exception):
        pass

    def __init__(self, handler, id):
        self.handler = handler
        self.id = id
        self.object = self.dereference(id)

    @property
    def current_user(self):
        return self.handler.current_user

    def get_user_domains(self):
        return UserAccess.get_domains(self.current_user)

    def get_object(self, id):
        if hasattr(self.model, "get_by_id"):
            return self.model.get_by_id(id)
        else:
            return self.model.objects.get(pk=id)

    @classmethod
    def redirect(cls, url):
        """
        Redirect to another card.
        Can only be called within dereference method
        :param url:
        :return:
        """
        raise cls.RedirectError(url)

    def dereference(self, id):
        """
        Resolve object by id.
        When redirect method called within, card will be redirected
        :param id:
        :return:
        """
        if self.model and id != "ajax":
            try:
                return self.get_object(id)
            except self.model.DoesNotExist:
                metrics["error", ("type", "no_such_object")] += 1
                raise self.NotFoundError()
        return None

    def get_data(self) -> Dict[str, Any]:
        """
        Returns template data
        """
        return {}

    def get_ajax_data(self, **kwargs):
        """
        Returns dynamic ajax variables
        """

    def get_template_name(self):
        """
        Calculate and return template name
        """
        return self.default_template_name

    def get_template(self):
        """
        Return Template instance
        """
        name = self.get_template_name()
        if name not in self.template_cache:
            self.template_cache[name] = None
            for p in self.TEMPLATE_PATH:
                tp = os.path.join(p, name + ".html.j2")
                if os.path.exists(tp):
                    env = Environment()
                    env.filters.update(
                        {
                            "managed_object_title": self.f_managed_object_title,
                            "service_title": self.f_service_title,
                            "logical_status": self.f_logical_status,
                            "timestamp": self.f_timestamp,
                            "glyph_summary": self.f_glyph_summary,
                            "object_location": self.f_object_location,
                            "object_console": self.f_object_console,
                        }
                    )
                    with open(tp) as f:
                        self.template_cache[name] = env.from_string(f.read())

        return self.template_cache[name]

    def render(self):
        template = self.get_template()
        if template:
            data = self.get_data()
            return template.render(**data)
        else:
            return None

    @classmethod
    def f_managed_object_title(cls, obj):
        """
        Convert managed object instance to title
        using profile card_title_template
        """
        title_tpl = obj.object_profile.card_title_template or cls.DEFAULT_MO_TITLE_TEMPLATE
        return Template(title_tpl).render({"object": obj})

    @classmethod
    def f_service_title(cls, obj):
        """
        Convert service object instance to title
        using profile card_title_template
        """
        title_tpl = obj.profile.card_title_template or cls.DEFAULT_SERVICE_TITLE_TEMPLATE
        return Template(title_tpl).render({"object": obj})

    @classmethod
    def f_timestamp(cls, ts):
        """
        Convert to readable timestamp like YYYY-MM-DD HH:MM:SS
        """
        if isinstance(ts, datetime.datetime):
            return ts.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ts

    @classmethod
    def f_logical_status(cls, s):
        return {
            "P": "Planned",
            "p": "Provisioning",
            "T": "Testing",
            "R": "Ready",
            "S": "Suspended",
            "r": "Removing",
            "C": "Closed",
            "U": "Unknown",
        }.get(s, "Unknown")

    @classmethod
    def f_glyph_summary(cls, s, collapse=False):
        def get_summary(d, profile):
            v = []
            if hasattr(profile, "show_in_summary"):

                def show_in_summary(p):
                    return p.show_in_summary

            else:

                def show_in_summary(p):
                    return True

            for p, c in sorted(d.items(), key=lambda x: -x[1]):
                pv = profile.get_by_id(p)
                if pv and show_in_summary(pv):
                    if collapse and c < 2:
                        badge = ""
                    else:
                        badge = ' <span class="badge">%s</span>' % c
                    order = getattr(pv, "display_order", 100)
                    v += [
                        (
                            (order, -c),
                            '<i class="%s" title="%s"></i>%s' % (pv.glyph, pv.name, badge),
                        )
                    ]
            return " ".join(i[1] for i in sorted(v, key=operator.itemgetter(0)))

        if not isinstance(s, dict):
            return ""
        r = []
        if "subscriber" in s:
            from noc.crm.models.subscriberprofile import SubscriberProfile

            r += [get_summary(s["subscriber"], SubscriberProfile)]
        if "service" in s:
            from noc.sa.models.serviceprofile import ServiceProfile

            r += [get_summary(s["service"], ServiceProfile)]
        if "fresh_alarms" in s and s["fresh_alarms"]:
            r += [
                '<i class="fa fa-exclamation-triangle"></i><span class="badge">%s</span>'
                % s["fresh_alarms"]["FreshAlarm"]
            ]
        r = [x for x in r if x]
        return "&nbsp;".join(r)

    @classmethod
    def f_object_location(cls, object):
        """
        Returns managed object location
        """
        from noc.inv.models.object import Object

        if isinstance(object, dict) and "container" in object:
            container = Object.get_by_id(object["container"]) if object["container"] else None
        else:
            container = object.container
        if not container:
            metrics["error", ("type", "no_such_container")] += 1
            return _("N/A")
        path = []
        c = container
        while c:
            if "address" in c.data:
                if c.data["address"]["text"]:
                    path += [c.data["address"]["text"]]
                    break
            if c.name:
                path += [c.name]
            c = c.container
            if c:
                c = Object.get_by_id(c.id)
        if not path:
            metrics["error", ("type", "no_such_path")] += 1
            return _("N/A")
        return ", ".join(reversed(path))

    @classmethod
    def f_object_console(cls, object):
        s = {1: "telnet", 2: "ssh", 3: "http", 4: "https"}[object.scheme]
        return "<a href='%s://%s/'><i class='fa fa-terminal'></i> %s</a>" % (
            s,
            object.address,
            s.upper(),
        )

    @staticmethod
    def update_dict(s, d):
        for k in d:
            if k in s:
                s[k] += d[k]
            else:
                s[k] = d[k]
