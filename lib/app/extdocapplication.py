# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ExtDocApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django moules
from django.http import HttpResponse
## NOC modules
from extapplication import ExtApplication, view
from noc.lib.serialize import json_encode, json_decode
from noc.lib.nosql import StringField, BooleanField, GeoPointField, Q
from noc.sa.interfaces import BooleanParameter, GeoPointParameter
from noc.lib.validators import is_int


class ExtDocApplication(ExtApplication):
    model = None  # Document to expose
    icon = "icon_application_view_list"
    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"
    int_query_fields = []  # Integer fields for exact match

    pk_field_name = None  # Set by constructor

    # REST return codes and messages
    OK = 200
    CREATED = 201
    DELETED = 204
    BAD_REQUEST = 400
    FORBIDDEN = 401
    NOT_FOUND = 404
    DUPLICATE_ENTRY = 409
    NOT_HERE = 410
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    THROTTLED = 503

    ignored_params = ["_dc"]
    page_param = "__page"
    start_param = "__start"
    limit_param = "__limit"
    sort_param = "__sort"
    format_param = "__format"  # List output format
    query_param = "__query"

    def __init__(self, *args, **kwargs):
        super(ExtDocApplication, self).__init__(*args, **kwargs)
        self.pk_field_name = "id"  # @todo: detect properly
        # Prepare field converters
        self.clean_fields = {}  # name -> Parameter
        for name, f in self.model._fields.items():
            if isinstance(f, BooleanField):
                self.clean_fields[name] = BooleanParameter()
            elif isinstance(f, GeoPointField):
                self.clean_fields[name] = GeoPointParameter()
        #
        if not self.query_fields:
            self.query_fields = ["%s__%s" % (n, self.query_condition)
                                 for n, f in self.model._fields.items()
                                 if f.unique and isinstance(f, StringField)]

    def get_Q(self, request, query):
        """
        Prepare Q statement for query
        """
        def get_q(f):
            if "__" not in f:
                return "%s__%s" % (f, self.query_condition)
            else:
                return f

        q = reduce(lambda x, y: x | Q(**{get_q(y):query}),
                   self.query_fields[1:],
                   Q(**{get_q(self.query_fields[0]): query}))
        if self.int_query_fields and is_int(query):
            v = int(query)
            for f in self.int_query_fields:
                q |= Q(**{f: v})
        return q

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        if query and self.query_fields:
            return self.model.objects.filter(self.get_Q(request, query))
        else:
            return self.model.objects.all()

    def deserialize(self, data):
        return json_decode(data)

    def response(self, content="", status=200):
        if not isinstance(content, basestring):
            return HttpResponse(json_encode(content),
                               mimetype="text/json; charset=utf-8",
                               status=status)
        else:
            return HttpResponse(content,
                               mimetype="text/plain; charset=utf-8",
                               status=status)

    def cleaned_query(self, q):
        q = q.copy()
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in (self.limit_param, self.page_param, self.start_param,
            self.format_param, self.sort_param, self.query_param):
            if p in q:
                del q[p]
        # Normalize parameters
        for p in q:
            if p in self.clean_fields:
                q[p] = self.clean_fields[p].clean(q[p])
        return q

    def instance_to_dict(self, o):
        r = {}
        for n, f in o._fields.items():
            v = getattr(o, n)
            if v is not None:
                v = f.to_python(v)
            if v is not None:
                if isinstance(f, GeoPointField):
                    pass
                elif type(v) not in (str, unicode, int, long, bool):
                    if hasattr(v, "id"):
                        v = v.id
                    else:
                        v = unicode(v)
            r[n] = v
        return r

    def instance_to_lookup(self, o):
        return {
            "id": str(o.id),
            "label": unicode(o)
        }

    def list_data(self, request, formatter):
        """
        Returns a list of requested object objects
        """
        q = dict(request.GET.items())
        limit = q.get(self.limit_param)
        # page = q.get(self.page_param)
        start = q.get(self.start_param)
        format = q.get(self.format_param)
        query = q.get(self.query_param)
        ordering = []
        if format == "ext" and self.sort_param in q:
            for r in self.deserialize(q[self.sort_param]):
                if r["direction"] == "DESC":
                    ordering += ["-%s" % r["property"]]
                else:
                    ordering += [r["property"]]
        q = self.cleaned_query(q)
        data = self.queryset(request, query).filter(**q)
        # Apply sorting
        if ordering:
            data = data.order_by(*ordering)
        if format == "ext":
            total = data.count()
        if start is not None and limit is not None:
            data = data[int(start):int(start) + int(limit)]
        out = [formatter(o) for o in data]
        if format == "ext":
            out = {
                "total": total,
                "success": True,
                "data": out
            }
        return self.response(out, status=self.OK)
        
    @view(method=["GET"], url="^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    @view(method=["GET"], url=r"^lookup/$", access="lookup", api=True)
    def api_lookup(self, request):
        return self.list_data(request, self.instance_to_lookup)

    @view(method=["POST"], url="^$", access="create", api=True)
    def api_create(self, request):
        try:
            attrs = self.deserialize(request.raw_post_data)
        except ValueError, why:
            return self.response(str(why), status=self.BAD_REQUEST)
        if "id" in attrs:
            del attrs["id"]
        try:
            self.queryset(request).get(**attrs)
            return self.response(status=self.DUPLICATE_ENTRY)
        except self.model.MultipleObjectsReturned:
            return self.response(status=self.DUPLICATE_ENTRY)
        except self.model.DoesNotExist:
            o = self.model(**attrs)
            o.save()
            return self.response(self.instance_to_dict(o), status=self.CREATED)

    @view(method=["GET"], url="^(?P<id>[0-9a-f]{24})/?$",
          access="read", api=True)
    def api_read(self, request, id):
        """
        Returns dict with object's fields and values
        """
        try:
            o = self.queryset(request).get(id=id)
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        return self.response(self.instance_to_dict(o), status=self.OK)

    @view(method=["PUT"], url="^(?P<id>[0-9a-f]{24})/?$",
          access="update", api=True)
    def api_update(self, request, id):
        try:
            attrs = self.deserialize(request.raw_post_data)
        except ValueError, why:
            return self.response(str(why), status=self.BAD_REQUEST)
        try:
            o = self.queryset(request).get(id=id)
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        for k, v in attrs.items():
            setattr(o, k, v)
        o.save()
        return self.response(status=self.OK)

    @view(method=["DELETE"], url="^(?P<id>[0-9a-f]{24})/?$",
          access="delete", api=True)
    def api_delete(self, request, id):
        try:
            o = self.queryset(request).get(id=id)
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        o.delete()
        return HttpResponse(status=self.DELETED)
