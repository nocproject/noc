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
from noc.lib.nosql import (StringField, BooleanField, GeoPointField,
                           ForeignKeyField, PlainReferenceField, Q)
from noc.sa.interfaces import (BooleanParameter, GeoPointParameter,
                               ModelParameter)
from noc.lib.validators import is_int


class ExtDocApplication(ExtApplication):
    model = None  # Document to expose
    icon = "icon_application_view_list"
    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"
    int_query_fields = []  # Integer fields for exact match
    pk_field_name = None  # Set by constructor

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
            elif isinstance(f, ForeignKeyField):
                self.clean_fields[f.name] = ModelParameter(
                    f.document_type, required=f.required)
        #
        if not self.query_fields:
            self.query_fields = ["%s__%s" % (n, self.query_condition)
                                 for n, f in self.model._fields.items()
                                 if f.unique and isinstance(f, StringField)]
        # Find field_* and populate custom fields
        self.custom_fields = {}
        for fn in [n for n in dir(self) if n.startswith("field_")]:
            h = getattr(self, fn)
            if callable(h):
                self.custom_fields[fn[6:]] = h

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
        return dict((str(k), data[k]) for k in data)

    def cleaned_query(self, q):
        q = q.copy()
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in (self.limit_param, self.page_param, self.start_param,
            self.format_param, self.sort_param, self.query_param,
            self.only_param):
            if p in q:
                del q[p]
        # Normalize parameters
        for p in q:
            if p in self.clean_fields:
                q[p] = self.clean_fields[p].clean(q[p])
        return q

    def instance_to_dict(self, o, fields=None):
        r = {}
        for n, f in o._fields.items():
            if fields and n not in fields:
                continue
            v = getattr(o, n)
            if v is not None:
                v = f.to_python(v)
            if v is not None:
                if isinstance(f, GeoPointField):
                    pass
                elif isinstance(f, ForeignKeyField):
                    r["%s__label" % f.name] = unicode(v)
                    v = v.id
                elif isinstance(f, PlainReferenceField):
                    r["%s__label" % f.name] = unicode(v)
                    if hasattr(v, "id"):
                        v = str(v.id)
                    else:
                        v = str(v)
                elif type(v) not in (str, unicode, int, long, bool):
                    if hasattr(v, "id"):
                        v = v.id
                    else:
                        v = unicode(v)
            r[n] = v
        # Add custom fields
        for f in self.custom_fields:
            r[f] = self.custom_fields[f](o)
        return r

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": unicode(o)
        }

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
        if "id" in attrs:
            del attrs["id"]
        try:
            self.queryset(request).get(**attrs)
            return self.response(status=self.CONFLICT)
        except self.model.MultipleObjectsReturned:
            return self.response(status=self.CONFLICT)
        except self.model.DoesNotExist:
            o = self.model(**attrs)
            o.save()
            format = request.GET.get(self.format_param)
            if format == "ext":
                r = {
                    "success": True,
                    "data": self.instance_to_dict(o)
                }
            else:
                r = self.instance_to_dict(o)
            return self.response(r, status=self.CREATED)

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
        only = request.GET.get(self.only_param)
        if only:
            only = only.split(",")
        return self.response(self.instance_to_dict(o, fields=only),
            status=self.OK)

    @view(method=["PUT"], url="^(?P<id>[0-9a-f]{24})/?$",
          access="update", api=True)
    def api_update(self, request, id):
        try:
            attrs = self.clean(self.deserialize(request.raw_post_data))
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
