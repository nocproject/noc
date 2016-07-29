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
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.lib.dateutils import humanize_distance
from noc.sa.interfaces.base import ModelParameter
from noc.core.scheduler.job import Job
from noc.core.translation import ugettext as _


class GetNowApplication(ExtApplication):
    """
    sa.getnow application
    """
    title = _("Get Now")
    menu = _("Get Now")
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
        qs = ManagedObject.objects
        if not request.user.is_superuser:
            qs = ManagedObject.objects.filter(UserAccess.Q(request.user))
        # qs = qs.exclude(name__startswith="wiping-")
        qs = qs.filter(is_managed=True).exclude(name="SAE").exclude(name__startswith="wiping-")
        mop = ManagedObjectProfile.objects.filter(enable_box_discovery_config=True)
        qs = qs.filter(object_profile__in=mop)
        if 'managed_object' in get_request_data:
            qs = qs.filter(id=int(get_request_data['managed_object']))
        if 'profile_name' in get_request_data:
            ids = ManagedObject.objects.filter(
                profile_name=get_request_data['profile_name']).values_list('id', flat=True)
            qs = qs.filter(id__in=ids)
        if 'administrative_domain' in get_request_data:
            ids = ManagedObject.objects.filter(administrative_domain=get_request_data['administrative_domain'])
            qs = qs.filter(id__in=ids)
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

    def instance_to_dict(self, mo, fields=None):
        job = Job.get_job_data("discovery",
                               jcls="noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                               key=mo.id,
                               pool=mo.pool.name
                               )
        last_update = mo.config.get_revisions(reverse=True)
        if last_update:
            last_update = humanize_distance(last_update[0].ts)
        last_success = '--'
        last_status = None
        if job:
            last_success = humanize_distance(job["last"]) if "last" in job else '--'
            last_status = job["ls"] if "ls" in job else None
        return {
            'id': str(mo.id),
            'name': mo.name,
            'profile_name': mo.profile_name,
            'last_success': last_success,
            'status': job["s"] if job else '--',
            'last_status': last_status,
            'last_update': last_update if last_update else None
        }
