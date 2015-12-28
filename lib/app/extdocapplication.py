# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ExtDocApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import uuid
## Django modules
from django.http import HttpResponse
## Third-party modules
from mongoengine.fields import (StringField, BooleanField, ListField,
                                EmbeddedDocumentField, ReferenceField,
                                BinaryField)
## NOC modules
from extapplication import ExtApplication, view
from noc.lib.nosql import (GeoPointField, ForeignKeyField,
                           PlainReferenceField, Q)
from noc.sa.interfaces.base import (
    BooleanParameter, GeoPointParameter,
    ModelParameter, ListOfParameter,
    EmbeddedDocumentParameter, DictParameter,
    InterfaceTypeError, DocumentParameter)
from noc.lib.validators import is_int, is_uuid
from noc.lib.serialize import json_decode
from noc.main.models.collectioncache import CollectionCache
from noc.main.models.doccategory import DocCategory


class ExtDocApplication(ExtApplication):
    model = None  # Document to expose
    icon = "icon_application_view_list"
    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"
    int_query_fields = []  # Integer fields for exact match
    clean_fields = {}  # field name -> Parameter instance
    parent_field = None  # Tree lookup
    parent_model = None

    def __init__(self, *args, **kwargs):
        super(ExtDocApplication, self).__init__(*args, **kwargs)
        self.pk = "id"  # @todo: detect properly
        self.has_uuid = False
        # Prepare field converters
        self.clean_fields = self.clean_fields.copy()  # name -> Parameter
        for name, f in self.model._fields.items():
            if isinstance(f, BooleanField):
                self.clean_fields[name] = BooleanParameter()
            elif isinstance(f, GeoPointField):
                self.clean_fields[name] = GeoPointParameter()
            elif isinstance(f, ForeignKeyField):
                self.clean_fields[f.name] = ModelParameter(
                    f.document_type, required=f.required)
            elif isinstance(f, ListField):
                if isinstance(f.field, EmbeddedDocumentField):
                    self.clean_fields[f.name] = ListOfParameter(
                        element=EmbeddedDocumentParameter(f.field.document_type))
            elif isinstance(f, ReferenceField):
                dt = f.document_type_obj
                if dt == "self":
                    dt = self.model
                self.clean_fields[f.name] = DocumentParameter(
                    dt,
                    required=f.required
                )
            if f.primary_key:
                self.pk = name
            if name == "uuid":
                self.has_uuid = True
        #
        if not self.query_fields:
            self.query_fields = ["%s__%s" % (n, self.query_condition)
                                 for n, f in self.model._fields.items()
                                 if f.unique and isinstance(f, StringField)]
        self.unique_fields = [
            n for n, f in self.model._fields.items() if f.unique
        ]
        # Install JSON API call when necessary
        self.json_collection = self.model._meta.get("json_collection")
        if (self.has_uuid and
                hasattr(self.model, "to_json") and
                not hasattr(self, "api_to_json") and
                not hasattr(self, "api_json")):
            self.add_view(
                "api_json",
                self._api_to_json,
                url="^(?P<id>[0-9a-f]{24})/json/$",
                method=["GET"], access="read", api=True)
            if self.json_collection and self.config.getboolean("develop", "install_collection"):
                self.add_view(
                    "api_install_json",
                    self._api_install_json,
                    url="^(?P<id>[0-9a-f]{24})/json/$",
                    method=["POST"], access="create", api=True)
        if self.json_collection:
            self.field_is_builtin = self._field_is_builtin
        # Find field_* and populate custom fields
        self.custom_fields = {}
        for fn in [n for n in dir(self) if n.startswith("field_")]:
            h = getattr(self, fn)
            if callable(h):
                self.custom_fields[fn[6:]] = h

    def get_custom_fields(self):
        from noc.main.models.customfield import CustomField
        return list(CustomField.table_fields(self.model._get_collection_name()))

    def get_launch_info(self, request):
        li = super(ExtDocApplication, self).get_launch_info(request)
        if self.json_collection:
            li["params"]["collection"] = self.json_collection
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
            if f == "uuid":
                if is_uuid(query):
                    return f
                else:
                    return None
            if "__" not in f:
                return "%s__%s" % (f, self.query_condition)
            else:
                return f

        qfx = [get_q(f) for f in self.query_fields]
        qfx = [x for x in qfx if x]
        q = reduce(lambda x, y: x | Q(**{get_q(y):query}),
                   qfx[1:],
                   Q(**{qfx[0]: query}))
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
        # @todo: correct __ lookups
        if any(p for p in q if p.endswith("__referred")):
            del q[p]
        return q

    def instance_to_dict(self, o, fields=None, nocustom=False):
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
                elif isinstance(f, ReferenceField):
                    r["%s__label" % f.name] = unicode(v)
                    if hasattr(v, "id"):
                        v = str(v.id)
                    else:
                        v = str(v)
                elif isinstance(f, ListField):
                    if (hasattr(f, "field") and
                            isinstance(f.field, EmbeddedDocumentField)):
                        v = [self.instance_to_dict(vv, nocustom=True) for vv in v]
                elif isinstance(f, BinaryField):
                    v = repr(v)
                elif type(v) not in (str, unicode, int, long, bool, dict):
                    if hasattr(v, "id"):
                        v = v.id
                    else:
                        v = unicode(v)
            r[n] = v
        # Add custom fields
        if not nocustom:
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

    @view(method=["GET"], url=r"^tree_lookup/$", access="lookup", api=True)
    def api_lookup_tree(self, request):
        def trim(s):
            return unicode(o).rsplit(" | ")[-1]

        if not self.parent_field:
            return None
        q = dict((str(k), v[0] if len(v) == 1 else v)
            for k, v in request.GET.lists())
        model = self.parent_model or self.model
        parent = q.get("parent")
        if not parent:
            qs = {"%s__exists" % self.parent_field: False}
        else:
            qs = {"%s" % self.parent_field: parent}
        if model == DocCategory:
            qs["type"] = DocCategory._senders[self.model]
        data = model.objects.filter(**qs)
        ordering = self.default_ordering
        if ordering:
            data = data.order_by(*ordering)
        count = data.count()
        data = [{"id": str(o.id), "label": trim(o)} for o in data]
        return {
            "total": count,
            "success": True,
            "data": data
        }

    @view(method=["POST"], url="^$", access="create", api=True)
    def api_create(self, request):
        try:
            attrs = self.clean(self.deserialize(request.raw_post_data))
        except ValueError, why:
            return self.response(str(why), status=self.BAD_REQUEST)

        if self.pk in attrs:
            del attrs[self.pk]
        if self.has_uuid and not attrs.get("uuid"):
            attrs["uuid"] = uuid.uuid4()
        # Check for duplicates
        if self.unique_fields:
            q = dict((k, attrs[k])
                     for k in self.unique_fields if k in attrs)
            if q:
                if self.queryset(request).filter(**q).first():
                    return self.response(status=self.CONFLICT)
        o = self.model()
        for k, v in attrs.items():
            if k != self.pk and "__" not in k:
                setattr(o, k, v)
        o.save()
        # Reread result
        o = self.model.objects.get(**{self.pk: o.pk})
        if request.is_extjs:
            r = {
                "success": True,
                "data": self.instance_to_dict(o)
            }
        else:
            r = self.instance_to_dict(o)
        return self.response(r, status=self.CREATED)

    @view(method=["GET"],
          url="^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
          access="read", api=True)
    def api_read(self, request, id):
        """
        Returns dict with object's fields and values
        """
        try:
            o = self.queryset(request).get(**{self.pk: id})
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        only = request.GET.get(self.only_param)
        if only:
            only = only.split(",")
        return self.response(self.instance_to_dict(o, fields=only),
                             status=self.OK)

    @view(method=["PUT"], url="^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
          access="update", api=True)
    def api_update(self, request, id):
        try:
            attrs = self.clean(self.deserialize(request.raw_post_data))
        except ValueError, why:
            return self.response(str(why), status=self.BAD_REQUEST)
        try:
            o = self.queryset(request).get(**{self.pk: id})
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        if self.has_uuid and not attrs.get("uuid") and not o.uuid:
            attrs["uuid"] = uuid.uuid4()
        # @todo: Check for duplicates
        for k in attrs:
            if k != self.pk and "__" not in k:
                setattr(o, k, attrs[k])
        o.save()
        # Reread result
        o = self.model.objects.get(**{self.pk: id})
        if request.is_extjs:
            r = {
                "success": True,
                "data": self.instance_to_dict(o)
            }
        else:
            r = self.instance_to_dict(o)
        return self.response(r, status=self.OK)

    @view(method=["DELETE"], url="^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
          access="delete", api=True)
    def api_delete(self, request, id):
        try:
            o = self.queryset(request).get(**{self.pk: id})
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        o.delete()
        return HttpResponse(status=self.DELETED)

    def _api_to_json(self, request, id):
        """
        Expose JSON collection item when available
        """
        o = self.get_object_or_404(self.model, id=id)
        return o.to_json()

    def _api_install_json(self, request, id):
        """
        Expose JSON collection item when available
        """
        from noc.lib.collection import Collection
        o = self.get_object_or_404(self.model, id=id)
        data = json_decode(o.to_json())
        dc = Collection(self.json_collection)
        dc.load()
        dc.install_item(data)
        dc.save()
        return True

    def _field_is_builtin(self, o):
        """
        Expose is_builtin field for JSON collections
        """
        return bool(CollectionCache.objects.filter(uuid=o.uuid))

    @view(url="^actions/group_edit/$", method=["POST"],
          access="update", api=True)
    def api_action_group_edit(self, request):
        validator = DictParameter(attrs={
            "ids": ListOfParameter(
                element=DocumentParameter(self.model),
                convert=True)
            }
        )
        rv = self.deserialize(request.raw_post_data)
        try:
            v = validator.clean(rv)
        except InterfaceTypeError, why:
            return self.render_json({
                "status": False,
                "message": "Bad request",
                "traceback": str(why)
            }, status=self.BAD_REQUEST)
        objects = v["ids"]
        del v["ids"]
        try:
            v = self.clean(v)
        except ValueError, why:
            return self.render_json({
                "status": False,
                "message": "Bad request",
                "traceback": str(why)
            }, status=self.BAD_REQUEST)
        for o in objects:
            for p in v:
                setattr(o, p, v[p])
            o.save()
        return "%d records has been updated" % len(objects)
