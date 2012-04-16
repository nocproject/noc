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
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
## Third-party modules
from tagging.models import Tag
## NOC modules
from extapplication import ExtApplication, view
from noc.lib.serialize import json_encode, json_decode
from noc.sa.interfaces import BooleanParameter, IntParameter, FloatParameter,\
    ModelParameter, StringParameter
from noc.lib.validators import is_int
from noc.sa.interfaces import InterfaceTypeError


class DjangoTagsParameter(StringParameter):
    def clean(self, value):
        if not value:
            return ""
        return ",".join(value)


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
    CONFLICT = 409
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
    custom_fields = {}  # name -> handler, populated automatically

    def __init__(self, *args, **kwargs):
        super(ExtModelApplication, self).__init__(*args, **kwargs)
        self.pk_field_name = self.model._meta.pk.name
        # Prepare field converters
        self.clean_fields = {}  # name -> Parameter
        for f in self.model._meta.fields:
            if f.name in self.clean_fields:
                continue  # Overriden behavior
            if f.name == "tags":
                self.clean_fields[f.name] = DjangoTagsParameter(
                    required=not f.null)
            elif isinstance(f, BooleanField):
                self.clean_fields[f.name] = BooleanParameter()
            elif isinstance(f, IntegerField):
                self.clean_fields[f.name] = IntParameter()
            elif isinstance(f, FloatField):
                self.clean_fields[f.name] = FloatParameter()
            elif isinstance(f, related.ForeignKey):
                self.clean_fields[f.name] = ModelParameter(f.rel.to,
                    required=not f.null)
            # Find field_* and populate custom fields
        self.custom_fields = {}
        for fn in [n for n in dir(self) if n.startswith("field_")]:
            h = getattr(self, fn)
            if callable(h):
                self.custom_fields[fn[6:]] = h
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
        return dict((str(k), data[k]) for k in data)

    def cleaned_query(self, q):
        nq = {}
        for p in q:
            if "__" in p:
                np, lt = p.split("__", 1)
            else:
                np, lt = p, None
                # Skip ignored params
            if np in self.ignored_params or p in (
                self.limit_param, self.page_param, self.start_param,
                self.format_param, self.sort_param, self.query_param):
                continue
            v = q[p]
            # Pass through interface cleaners
            if lt == "referred":
                # Unroll __referred
                app, fn = v.split("__", 1)
                model = self.site.apps[app].model
                extra_where = "%s.\"%s\" IN (SELECT \"%s\" FROM %s)" % (
                    self.model._meta.db_table, self.model._meta.pk.name,
                    model._meta.get_field_by_name(fn)[0].attname,
                    model._meta.db_table
                    )
                if None in nq:
                    nq[None] += [extra_where]
                else:
                    nq[None] = [extra_where]
                continue
            elif lt and hasattr(self, "lookup_%s" % lt):
                # Custom lookup
                getattr(self, "lookup_%s" % lt)(nq, np, v)
                continue
            elif np in self.clean_fields:  # @todo: Check for valid lookup types
                v = self.clean_fields[np].clean(v)
                # Write back
            nq[p] = v
        return nq

    def instance_to_dict(self, o):
        r = {}
        for f in o._meta.local_fields:
            if f.name == "tags":
                # Send tags as a list
                r[f.name] = [x for x in
                             getattr(o, f.name).split(",") if x]
            elif f.rel is None:
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
            # Add custom fields
        for f in self.custom_fields:
            r[f] = self.custom_fields[f](o)
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
        # Todo: Fix
        q = dict((str(k), v[0] if len(v) == 1 else v)
        for k, v in request.GET.lists())
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
        if None in q:
            ew = q.pop(None)
            data = self.queryset(request, query).filter(**q).extra(where=ew)
        else:
            data = self.queryset(request, query).filter(**q)
        data = data.select_related()
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

    def lookup_tags(self, q, name, value):
        if not value:
            return
        if isinstance(value, basestring):
            value = [value]
        a, m = self.model._meta.db_table.split("_", 1)
        tags = Tag.objects.filter(name__in=value).values_list("id", flat=True)
        if len(tags) != len(value):
            s = "FALSE"
        else:
            ct_id = ContentType.objects.get(app_label=a, model=m).id
            s = """
                (%(table)s.id IN (
                    SELECT object_id
                    FROM tagging_taggeditem
                    WHERE
                        content_type_id = %(ct_id)d
                        AND tag_id in (%(tags)s)
                    GROUP BY object_id
                    HAVING COUNT(object_id) = %(t_len)s
                ))""" % {
                "table": self.model._meta.db_table,
                "ct_id": ct_id,
                "tags": ", ".join(str(t) for t in tags),
                "t_len": len(value)
            }
        if None in q:
            q[None] += [s]
        else:
            q[None] = [s]

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
            return self.render_json(
                    {
                    "status": False,
                    "message": "Duplicated record"
                },
                status=self.CONFLICT)
        except self.model.MultipleObjectsReturned:
            return self.render_json(
                    {
                    "status": False,
                    "message": "Duplicated record"
                }, status=self.CONFLICT)
        except self.model.DoesNotExist:
            o = self.model(**attrs)
            try:
                o.save()
            except IntegrityError:
                return self.render_json(
                        {
                        "status": False,
                        "message": "Integrity error"
                    }, status=self.CONFLICT)
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
            return self.render_json(
                    {
                    "status": False,
                    "message": "Bad request",
                    "traceback": str(why)
                }, status=self.BAD_REQUEST)
        except InterfaceTypeError, why:
            return self.render_json(
                    {
                    "status": False,
                    "message": "Bad request",
                    "traceback": str(why)
                }, status=self.BAD_REQUEST)
        try:
            o = self.queryset(request).get(id=int(id))
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        for k, v in attrs.items():
            setattr(o, k, v)
        try:
            o.save()
        except IntegrityError:
            return self.render_json(
                    {
                    "status": False,
                    "message": "Integrity error"
                }, status=self.CONFLICT)
        return self.response(status=self.OK)

    @view(method=["DELETE"], url="^(?P<id>\d+)/?$", access="delete", api=True)
    def api_delete(self, request, id):
        try:
            o = self.queryset(request).get(id=int(id))
        except self.model.DoesNotExist:
            return self.render_json({
                "status": False,
                "message": "Not found"
            }, status=self.NOT_FOUND)
        o.delete()  # @todo: Detect errors
        return HttpResponse(status=self.DELETED)
