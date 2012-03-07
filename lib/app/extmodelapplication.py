# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ExtModelApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django moules
from django.http import HttpResponse
from django.db.models.fields import CharField, BooleanField, IntegerField,\
                                    FloatField, related
from django.db.models import Q
## NOC modules
from extapplication import ExtApplication, view
from noc.lib.serialize import json_encode, json_decode
from noc.sa.interfaces import BooleanParameter, IntParameter, FloatParameter,\
                              ModelParameter
from noc.lib.validators import is_int
from noc.sa.interfaces import InterfaceTypeError


class ExtModelApplication(ExtApplication):
    model = None  # Django model to expose
    icon = "icon_application_view_list"
    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"  # Match method for string fields
    int_query_fields = []  # Query integer fields for exact match

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
    clean_fields = {}  # field name -> Parameter instance

    def __init__(self, *args, **kwargs):
        super(ExtModelApplication, self).__init__(*args, **kwargs)
        self.pk_field_name = self.model._meta.pk.name
        # Prepare field converters
        self.clean_fields = {}  # name -> Parameter
        for f in self.model._meta.fields:
            if f.name in self.clean_fields:
                continue  # Overriden behavior
            if isinstance(f, BooleanField):
                self.clean_fields[f.name] = BooleanParameter()
            elif isinstance(f, IntegerField):
                self.clean_fields[f.name] = IntParameter()
            elif isinstance(f, FloatField):
                self.clean_fields[f.name] = FloatParameter()
            elif isinstance(f, related.ForeignKey):
                self.clean_fields[f.name] = ModelParameter(f.rel.to)
        #
        if not self.query_fields:
            # By default - search in unique text fields
            self.query_fields = ["%s__%s" % (f.name, self.query_condition)
                                 for f in self.model._meta.fields
                                 if f.unique and isinstance(f, CharField)]

    def get_Q(self, request, query):
        """
        Prepare Q statement for query
        """
        def get_q(f):
            if "__" not in f:
                return "%s__%s" % (f, self.query_condition)
            else:
                return f

        q = reduce(lambda x, y: x | Q(**{get_q(y): query}),
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

    def clean(self, data):
        """
        Clean up input data
        :param data: dict of parameters
        :type data: dict
        :return: dict of cleaned parameters of raised InterfaceTypeError
        :rtype: dict
        """
        if "id" in data:
            del data["id"]
        for f in data:
            if f in self.clean_fields:
                data[f] = self.clean_fields[f].clean(data[f])
        return data

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
        for f in o._meta.local_fields:
            if f.rel is None:
                v = f._get_val_from_obj(o)
                if (v is not None and
                    type(v) not in (str, unicode, int, long, bool)):
                    v = unicode(v)
                r[f.name] = v
            else:
                v = getattr(o, f.name)
                if v:
                    r[f.name] = v._get_pk_val()
                    r["%s__label" % f.name] = unicode(v)
                else:
                    r[f.name] = None
                    r["%s__label" % f.name] = ""
        return r

    def instance_to_lookup(self, o):
        return {
            "id": o.id,
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
            attrs = self.clean(self.deserialize(request.raw_post_data))
        except ValueError, why:
            return self.response(str(why), status=self.BAD_REQUEST)
        except InterfaceTypeError, why:
            return self.response(str(why), status=self.BAD_REQUEST)
        try:
            self.queryset(request).get(**attrs)
            return self.response(status=self.DUPLICATE_ENTRY)
        except self.model.MultipleObjectsReturned:
            return self.response(status=self.DUPLICATE_ENTRY)
        except self.model.DoesNotExist:
            o = self.model(**attrs)
            o.save()
            return self.response(self.instance_to_dict(o), status=self.CREATED)

    @view(method=["GET"], url="^(?P<id>\d+)/?$", access="read", api=True)
    def api_read(self, request, id):
        """
        Returns dict with object's fields and values
        """
        try:
            o = self.queryset(request).get(id=int(id))
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        return self.response(self.instance_to_dict(o), status=self.OK)

    @view(method=["PUT"], url="^(?P<id>\d+)/?$", access="update", api=True)
    def api_update(self, request, id):
        try:
            attrs = self.clean(self.deserialize(request.raw_post_data))
        except ValueError, why:
            return self.response(str(why), status=self.BAD_REQUEST)
        except InterfaceTypeError, why:
            return self.response(str(why), status=self.BAD_REQUEST)
        try:
            o = self.queryset(request).get(id=int(id))
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        print attrs
        for k, v in attrs.items():
            setattr(o, k, v)
        o.save()
        return self.response(status=self.OK)

    @view(method=["DELETE"], url="^(?P<id>\d+)/?$", access="delete", api=True)
    def api_delete(self, request, id):
        try:
            o = self.queryset(request).get(id=int(id))
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        o.delete()
        return HttpResponse(status=self.DELETED)

    @view(method=["GET"], url="^filter/(?P<var>[^/]+)/$",
          access="read", api=True)
    def api_filter(self, request, var):
        q = request.GET.get(self.query_param).lower()
        g = lambda o: getattr(o, var)
        d = [{"id": g(o).id, "label": unicode(g(o))}
                for o in self.model.objects.distinct(var)]
        if q:
            d = [x for x in d if q in x["label"].lower()]
        d = sorted(d, key=lambda x: x["label"])
        return d
