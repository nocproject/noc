# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ExtModelApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django moules
from django.http import HttpResponse
from django.db.models.fields import (
    CharField, BooleanField, IntegerField, FloatField,
    DateField, DateTimeField, related)
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
## NOC modules
from extapplication import ExtApplication, view
from noc.sa.interfaces import (BooleanParameter, IntParameter,
                               FloatParameter, ModelParameter,
                               StringParameter, TagsParameter,
                               NoneParameter, StringListParameter)
from interfaces import DateParameter, DateTimeParameter
from noc.lib.validators import is_int
from noc.sa.interfaces import InterfaceTypeError
from noc.lib.db import QTags


class ExtModelApplication(ExtApplication):
    model = None  # Django model to expose
    icon = "icon_application_view_list"
    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"  # Match method for string fields
    int_query_fields = []  # Query integer fields for exact match
    pk_field_name = None  # Set by constructor
    clean_fields = {}  # field name -> Parameter instance
    custom_fields = {}  # name -> handler, populated automatically

    def __init__(self, *args, **kwargs):
        super(ExtModelApplication, self).__init__(*args, **kwargs)
        self.db_table = self.model._meta.db_table
        self.pk_field_name = self.model._meta.pk.name
        self.pk = self.pk_field_name
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
        # m2m fields
        self.m2m_fields = {}  # Name -> Model
        for f in self.model._meta.many_to_many:
            self.m2m_fields[f.name] = f.rel.to
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

    def get_validator(self, field):
        """
        Returns Parameter instance or None to clean up field
        :param field:
        :type field: Field
        :return:
        """
        from noc.lib.fields import TagsField, TextArrayField

        if isinstance(field, BooleanField):
            return BooleanParameter()
        elif isinstance(field, IntegerField):
            return IntParameter()
        elif isinstance(field, FloatField):
            return FloatParameter()
        elif isinstance(field, DateField):
            return DateParameter()
        elif isinstance(field, DateTimeField):
            return DateTimeParameter()
        elif isinstance(field, TagsField):
            return TagsParameter(required=not field.null)
        elif isinstance(field, TextArrayField):
            return StringListParameter(required=not field.null)
        elif isinstance(field, related.ForeignKey):
            self.fk_fields[field.name] = field.rel.to
            return ModelParameter(field.rel.to,
                required=not field.null)
        else:
            return None

    def fav_convert(self, item):
        """
        Convert favorite item from string to storage format
        """
        return int(item)

    def get_custom_fields(self):
        from noc.main.models.customfield import CustomField
        return list(CustomField.table_fields(self.model._meta.db_table))

    def get_launch_info(self, request):
        li = super(ExtModelApplication, self).get_launch_info(request)
        cf = self.get_custom_fields()
        if cf:
            li["params"].update({
                "cust_model_fields": [f.ext_model_field for f in cf],
                "cust_grid_columns": [f.ext_grid_column for f in cf],
                "cust_form_fields": [f.ext_form_field for f in cf
                                     if not f.is_hidden]
            })
        return li

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

    def clean(self, data):
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
        # Clean up fields
        for f in self.clean_fields:
            if f in data:
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
        # Add m2m fields
        for n in self.m2m_fields:
            r[n] = list(getattr(o, n).values_list("id", flat=True))
        # Add custom fields
        for f in self.custom_fields:
            if fields and f not in fields:
                continue
            r[f] = self.custom_fields[f](o)
        return r

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": o.id,
            "label": unicode(o)
        }

    def lookup_tags(self, q, name, value):
        if not value:
            return
        if isinstance(value, basestring):
            value = [value]
        tq = ("%%s::text[] <@ %s.tags" % self.db_table, [value])
        if None in q:
            q[None] += [tq]
        else:
            q[None] = [tq]

    def update_m2m(self, o, name, values):
        if values is None:
            return  # Do not touch
        m = self.m2m_fields[name]
        f = getattr(o, name)
        # Existing m2m relations
        e_values = set(f.values_list("id", flat=True))
        n_values = set(values)
        # Delete left relations
        for v in e_values - n_values:
            f.remove(m.objects.get(id=v))
        # Create new relations
        for v in n_values - e_values:
            f.add(m.objects.get(id=v))

    def update_m2ms(self, o, attrs):
        """
        Update all m2m fields
        """
        for f in self.m2m_fields:
            if f in attrs:
                self.update_m2m(o, f, attrs[f])

    def split_mtm(self, pdata):
        """
        Split post data to (fields, m2mfields) data
        """
        if self.m2m_fields:
            f = {}
            m2m = {}
            for n in pdata:
                if n in self.m2m_fields:
                    m2m[n] = pdata[n]
                else:
                    f[n] = pdata[n]
            return f, m2m
        else:
            return pdata, {}

    @view(method=["GET"], url="^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    @view(method=["GET"], url=r"^lookup/$", access="lookup", api=True)
    def api_lookup(self, request):
        return self.list_data(request, self.instance_to_lookup)

    @view(method=["POST"], url="^$", access="create", api=True)
    def api_create(self, request):
        attrs, m2m_attrs = self.split_mtm(
            self.deserialize(request.raw_post_data))
        try:
            attrs = self.clean(attrs)
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
            # Exclude callable values from query
            # (Django raises exception on pyRules)
            # @todo: Check unique fields only?
            qattrs = dict((k, attrs[k])
                for k in attrs if not callable(attrs[k]))
            # Check for duplicates
            self.queryset(request).get(**qattrs)
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
                if m2m_attrs:
                    self.update_m2ms(o, m2m_attrs)
            except IntegrityError:
                return self.render_json(
                        {
                        "status": False,
                        "message": "Integrity error"
                    }, status=self.CONFLICT)
            # Check format
            format = request.GET.get(self.format_param)
            if format == "ext":
                r = {
                    "success": True,
                    "data": self.instance_to_dict(o)
                }
            else:
                r = self.instance_to_dict(o)
            return self.response(r, status=self.CREATED)

    @view(method=["GET"], url="^(?P<id>\d+)/?$", access="read", api=True)
    def api_read(self, request, id):
        """
        Returns dict with object's fields and values
        """
        try:
            o = self.queryset(request).get(id=int(id))
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        only = request.GET.get(self.only_param)
        if only:
            only = only.split(",")
        return self.response(self.instance_to_dict(o, fields=only),
            status=self.OK)

    @view(method=["PUT"], url="^(?P<id>\d+)/?$", access="update", api=True)
    def api_update(self, request, id):
        attrs, m2m_attrs = self.split_mtm(
            self.deserialize(request.raw_post_data))
        try:
            attrs = self.clean(attrs)
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
            if m2m_attrs:
                self.update_m2ms(o, m2m_attrs)
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
