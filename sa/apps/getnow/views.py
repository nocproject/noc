# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.groupaccess application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

#  # NOC modules
from noc.lib.app import view, ExtApplication
from noc.sa.models.managedobject import ManagedObject
from noc.lib.dateutils import humanize_distance
from noc.sa.interfaces.base import ModelParameter


class GetNowApplication(ExtApplication):
    """
    sa.getnow application
    """
    title = "Get Now"
    menu = "Get Now"
    icon = "icon_monitor"

    ignored_params = ["status", "_dc", "managed_object", "profile_name", "administrative_domain"]

    clean_fields = {
        "managed_object": ModelParameter(ManagedObject)
    }

    @view("^$", method=["GET"], access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        get_request_data = request.GET
        qs = DiscoveryJob.objects.filter(jcls='config_discovery').order_by('status')
        if 'managed_object' in get_request_data:
            qs = qs.filter(object=int(get_request_data['managed_object']))
        if 'profile_name' in get_request_data:
            ids = ManagedObject.objects.filter(
                profile_name=get_request_data['profile_name']).values_list('id', flat=True)
            qs = qs.filter(object__in=ids)
        if 'administrative_domain' in get_request_data:
            ids = ManagedObject.objects.filter(administrative_domain=get_request_data['administrative_domain'])
            qs = qs.filter(object__in=ids)
        return qs

    def cleaned_query(self, q):
        to_clean_up = (self.limit_param, self.page_param, self.start_param,
                       self.format_param, self.sort_param, self.query_param,
                       self.only_param)
        q = q.copy()
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in to_clean_up:
            if p in q:
                del q[p]
        for p in q:
            qp = p.split("__")[0]
            if qp in self.clean_fields:
                q[p] = self.clean_fields[qp].form_clean(q[p])
        return q

    def instance_to_dict(self, o, fields=None):
        last_success = humanize_distance(o.ts) if o.ts else '--'
        mo = ManagedObject.objects.get(id = o.object)
        last_update = mo.config.get_revisions(reverse=True)
        if last_update:
            last_update = humanize_distance(last_update[0].ts)
        return {
            'id': str(mo.id),
            'name': mo.name,
            'profile_name': mo.profile_name,
            'last_success': last_success,
            'status': o.status,
            'last_status': o.last_status,
            'last_update': last_update if last_update else None
        }
