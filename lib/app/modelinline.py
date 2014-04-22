# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ModelInline
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db.models.fields import CharField, BooleanField, IntegerField,\
    FloatField, related
from django.db.models import Q
from django.db.utils import IntegrityError
## NOC modules
from noc.sa.interfaces import (BooleanParameter, IntParameter,
                               FloatParameter, ModelParameter,
                               StringParameter, TagsParameter,
                               StringListParameter,
                               NoneParameter, InterfaceTypeError)
from noc.lib.validators import is_int
from noc.lib.fields import TextArrayField


class ModelInline(object):
    ## HTTP Result Codes
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
    ## Recognized GET parameters
    ignored_params = ["_dc"]
    page_param = "__page"
    start_param = "__start"
    limit_param = "__limit"
    sort_param = "__sort"
    format_param = "__format"  # List output format
    query_param = "__query"
    only_param = "__only"

    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"  # Match method for string fields
    int_query_fields = []  # Query integer fields for exact match
    pk_field_name = None  # Set by constructor
    clean_fields = {}  # field name -> Parameter instance
    custom_fields = {}  # name -> handler, populated automatically

    def __init__(self, model):
        self.model = model
        self.app = None
        self.pk_field_name = self.model._meta.pk.name
        # Prepare field converters
        self.clean_fields = self.clean_fields.copy()  # name -> Parameter
        self.fk_fields = {}
        for f in self.model._meta.fields:
            if f.name in self.clean_fields:
                continue  # Overriden behavior
            vf = self.get_validator(f)
            if vf:
                if f.null:
                    vf = NoneParameter() | vf
                self.clean_fields[f.name] = vf
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
        # Add searchable custom fields
        self.query_fields += ["%s__%s" % (f.name, self.query_condition)
            for f in self.get_custom_fields() if f.is_searchable]
        #

    def contribute_to_class(self, app, name):
        # Add List handler
        app.add_view("api_%s_list" % name, self.api_list,
            method=["GET"],
            url="^(?P<parent>[^/]+)/%s/$" % name,
            access="read", api=True)
        # Add Create handler
        app.add_view("api_%s_create" % name, self.api_create,
            method=["POST"],
            url="^(?P<parent>[^/]+)/%s/$" % name,
            access="create", api=True)
        # Add Read Handler
        app.add_view("api_%s_read" % name, self.api_read,
            method=["GET"],
            url="^(?P<parent>[^/]+)/%s/(?P<id>\d+)/?$" % name,
            access="read", api=True)
        # Add Update Handler
        app.add_view("api_%s_update" % name, self.api_update,
            method=["PUT"],
            url="^(?P<parent>[^/]+)/%s/(?P<id>\d+)/?$" % name,
            access="update", api=True)
        # Add Delete Handler
        app.add_view("api_%s_delete" % name, self.api_delete,
            method=["DELETE"],
            url="^(?P<parent>[^/]+)/%s/(?P<id>\d+)/?$" % name,
            access="delete", api=True)

    def set_app(self, app):
        self.app = app
        self.parent_model = self.app.model
        self.parent_rel = None
        for f in self.model._meta.fields:
            if f.rel and f.rel.to and f.rel.to == self.parent_model:
                self.parent_rel = f.name
                break
        assert self.parent_rel
        if self.parent_rel in self.clean_fields:
            del self.clean_fields[self.parent_rel]

    def get_custom_fields(self):
        from noc.main.models import CustomField
        return list(CustomField.table_fields(self.model._meta.db_table))

    def get_validator(self, field):
        """
        Returns Parameter instance or None to clean up field
        :param field:
        :type field: Field
        :return:
        """
        from noc.lib.fields import AutoCompleteTagsField

        if isinstance(field, BooleanField):
            return BooleanParameter()
        elif isinstance(field, IntegerField):
            return IntParameter()
        elif isinstance(field, FloatField):
            return FloatParameter()
        elif isinstance(field, AutoCompleteTagsField):
            return TagsParameter(required=not field.null)
        elif isinstance(field, TextArrayField):
            return StringListParameter(required=not field.null)
        elif isinstance(field, related.ForeignKey):
            self.fk_fields[field.name] = field.rel.to
            return ModelParameter(field.rel.to,
                required=not field.null)
        else:
            return None

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

    def clean(self, data, parent):
        """
        Clean up input data
        :param data: dict of parameters
        :type data: dict
        :return: dict of cleaned parameters of raised InterfaceTypeError
        :rtype: dict
        """
        # Delete id
        if "id" in data:
            del data["id"]
        # Forcefully set parent
        data[self.parent_rel] = parent
        # Clean up fields
        for f in self.clean_fields:
            if f in data and f != self.parent_rel:
                data[f] = self.clean_fields[f].clean(data[f])
        # Dereference fields
        refs = [f for f in data if "__" in f]
        for r in refs:
            l, x = r.split("__", 1)
            if l in self.fk_fields:
                try:
                    data[l] = self.fk_fields[l].objects.get(**{x: data[r]})
                except self.fk_fields[l].DoesNotExist:
                    # Raise error
                    data[l] = self.clean_fields[l].clean(0)
                del data[r]  # Dereferenced
        # Clone data
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
                self.format_param, self.sort_param, self.query_param,
                self.only_param):
                continue
            v = q[p]
            if v == "\x00":
                v = None
            # Pass through interface cleaners
            if lt == "referred":
                # Unroll __referred
                app, fn = v.split("__", 1)
                model = self.app.site.apps[app].model
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
            elif np in self.fk_fields and lt:
                # dereference
                try:
                    nq[np] = self.fk_fields[np].objects.get(**{lt: v})
                except self.fk_fields[np].DoesNotExist:
                    nq[np] = 0  # False search
                continue
            elif np in self.clean_fields:  # @todo: Check for valid lookup types
                v = self.clean_fields[np].clean(v)
                # Write back
            nq[p] = v
        return nq

    def instance_to_dict(self, o, fields=None):
        r = {}
        for f in o._meta.local_fields:
            if fields and f.name not in fields:
                continue  # Restrict to selected fields
            if f.name == "tags":
                # Send tags as a list
                r[f.name] = getattr(o, f.name)
            elif f.rel is None:
                v = f._get_val_from_obj(o)
                if (v is not None and
                    type(v) not in (str, unicode, int, long, bool, list)):
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
            if fields and f not in fields:
                continue
            r[f] = self.custom_fields[f](o)
        return r

    def list_data(self, request, formatter, parent=None):
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
        only = q.get(self.only_param)
        if only:
            only = only.split(",")
        ordering = []
        if format == "ext" and self.sort_param in q:
            for r in self.app.deserialize(q[self.sort_param]):
                if r["direction"] == "DESC":
                    ordering += ["-%s" % r["property"]]
                else:
                    ordering += [r["property"]]
        q = self.cleaned_query(q)
        if parent:
            q["%s__id" % self.parent_rel] = parent
        if None in q:
            ew = q.pop(None)
            data = self.queryset(request, query).filter(**q).extra(where=ew)
        else:
            data = self.queryset(request, query).filter(**q)
        if hasattr(data, "_as_sql"):  # For Models only
            data = data.select_related()
        # Apply sorting
        if ordering:
            data = data.order_by(*ordering)
        if format == "ext":
            total = data.count()
        if start is not None and limit is not None:
            data = data[int(start):int(start) + int(limit)]
        out = [formatter(o, fields=only) for o in data]
        if format == "ext":
            out = {
                "total": total,
                "success": True,
                "data": out
            }
        return self.app.response(out, status=self.OK)

    def api_list(self, request, parent):
        return self.list_data(request, self.instance_to_dict,
            parent=int(parent))

    def api_create(self, request, parent):
        parent = self.app.get_object_or_404(
            self.parent_model, id=int(parent))
        try:
            attrs = self.clean(self.app.deserialize(request.raw_post_data), parent)
        except ValueError, why:
            return self.app.render_json(
                    {
                        "status": False,
                        "message": "Bad request",
                        "traceback": str(why)
                    }, status=self.app.BAD_REQUEST)
        except InterfaceTypeError, why:
            return self.app.render_json(
                    {
                        "status": False,
                        "message": "Bad request",
                        "traceback": str(why)
                    }, status=self.BAD_REQUEST)
        try:
            # Exclude callable values from query
            # (Django raises exception on pyRules)
            # @todo: Check unique fields only?
            qattrs = dict((k, attrs[k])
                for k in attrs if not callable(attrs[k]))
            # Check for duplicates
            self.queryset(request).get(**qattrs)
            return self.app.render_json(
                    {
                    "status": False,
                    "message": "Duplicated record"
                },
                status=self.CONFLICT)
        except self.model.MultipleObjectsReturned:
            return self.app.render_json(
                    {
                    "status": False,
                    "message": "Duplicated record"
                }, status=self.CONFLICT)
        except self.model.DoesNotExist:
            attrs[self.parent_rel] = parent
            o = self.model(**attrs)
            try:
                o.save()
            except IntegrityError:
                return self.app.render_json(
                        {
                        "status": False,
                        "message": "Integrity error"
                    }, status=self.CONFLICT)
            format = request.GET.get(self.format_param)
            if format == "ext":
                r = {
                    "success": True,
                    "data": self.instance_to_dict(o)
                }
            else:
                r = self.instance_to_dict(o)
            return self.app.response(r, status=self.CREATED)

    def api_read(self, request, parent, id):
        """
        Returns dict with object's fields and values
        """
        try:
            o = self.queryset(request).get(
                id=int(id), parent__id=int(parent))
        except self.model.DoesNotExist:
            return self.app.response("", status=self.NOT_FOUND)
        only = request.GET.get(self.only_param)
        if only:
            only = only.split(",")
        return self.app.response(self.instance_to_dict(o, fields=only),
            status=self.OK)

    def api_update(self, request, parent, id):
        parent = self.app.get_object_or_404(
            self.parent_model, id=int(parent))
        try:
            attrs = self.clean(self.app.deserialize(request.raw_post_data), parent)
        except ValueError, why:
            return self.app.render_json(
                    {
                    "status": False,
                    "message": "Bad request",
                    "traceback": str(why)
                }, status=self.BAD_REQUEST)
        except InterfaceTypeError, why:
            return self.app.render_json(
                    {
                    "status": False,
                    "message": "Bad request",
                    "traceback": str(why)
                }, status=self.BAD_REQUEST)
        try:
            o = self.queryset(request).get(id=int(id))
        except self.model.DoesNotExist:
            return self.app.response("", status=self.NOT_FOUND)
        attrs[self.parent_rel] = parent
        for k, v in attrs.items():
            setattr(o, k, v)
        try:
            o.save()
        except IntegrityError:
            return self.app.render_json(
                    {
                    "status": False,
                    "message": "Integrity error"
                }, status=self.CONFLICT)
        return self.app.response(status=self.OK)

    def api_delete(self, request, parent, id):
        try:
            q = {
                "id": int(id),
                "%s__id" % self.parent_rel: int(parent)
            }
            o = self.queryset(request).get(**q)
        except self.model.DoesNotExist:
            return self.app.render_json({
                "status": False,
                "message": "Not found"
            }, status=self.NOT_FOUND)
        o.delete()  # @todo: Detect errors
        return self.app.response("", status=self.DELETED)
