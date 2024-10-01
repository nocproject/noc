# ---------------------------------------------------------------------
# ExtDocApplication implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import uuid
from functools import reduce
import os

# Third-party modules
from django.http import HttpResponse
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    EmbeddedDocumentField,
    ReferenceField,
    BinaryField,
    DynamicField,
    GeoPointField,
    EnumField,
    EmbeddedDocumentListField,
    ObjectIdField,
)
from mongoengine.errors import ValidationError, NotUniqueError
from mongoengine.queryset import Q

# NOC modules
from noc.core.mongo.fields import (
    DateField,
    ForeignKeyField,
    PlainReferenceField,
    ForeignKeyListField,
    PlainReferenceListField,
)
from noc.sa.interfaces.base import (
    BooleanParameter,
    GeoPointParameter,
    ModelParameter,
    ListOfParameter,
    EmbeddedDocumentParameter,
    DictParameter,
    InterfaceTypeError,
    DocumentParameter,
    ObjectIdParameter,
)
from noc.core.validators import is_int, is_uuid
from noc.aaa.models.permission import Permission
from noc.aaa.models.modelprotectionprofile import ModelProtectionProfile
from noc.core.middleware.tls import get_user
from noc.main.models.doccategory import DocCategory
from noc.main.models.label import Label
from noc.core.collection.base import Collection
from noc.core.comp import smart_text
from noc.models import get_model_id
from .extapplication import ExtApplication, view


class ExtDocApplication(ExtApplication):
    model = None  # Document to expose
    icon = "icon_application_view_list"
    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"
    int_query_fields = []  # Integer fields for exact match
    clean_fields = {"id": ObjectIdParameter()}  # field name -> Parameter instance
    parent_field = None  # Tree lookup
    parent_model = None
    secret_fields = (
        None  # Set of sensitive fields. "secret" permission is required to show of modify
    )
    lookup_default = [{"id": "Leave unchanged", "label": "Leave unchanged"}]
    ignored_fields = {"id", "bi_id", "state"}
    SECRET_MASK = "********"
    # Add `__label` items
    field_labels = {}  # field_name -> callable(field_value) -> result

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pk = "id"  # @todo: detect properly
        self.has_uuid = False
        # Prepare field converters
        self.clean_fields = self.clean_fields.copy()  # name -> Parameter
        for name, f in self.model._fields.items():
            if isinstance(f, BooleanField):
                self.clean_fields[name] = BooleanParameter()
            elif isinstance(f, GeoPointField):
                self.clean_fields[name] = GeoPointParameter()
            elif isinstance(f, ForeignKeyListField):
                self.clean_fields[f.name] = ListOfParameter(element=ModelParameter(f.document_type))
            # elif isinstance(f, PlainReferenceListField):
            #     self.clean_fields[f.name] = ListOfParameter(element=ModelParameter(f.document_type))
            elif isinstance(f, ForeignKeyField):
                self.clean_fields[f.name] = ModelParameter(f.document_type, required=f.required)
            elif isinstance(f, EmbeddedDocumentListField):
                self.clean_fields[f.name] = ListOfParameter(
                    element=EmbeddedDocumentParameter(f.field.document_type)
                )
            elif isinstance(f, ListField):
                if isinstance(f.field, EmbeddedDocumentField):
                    self.clean_fields[f.name] = ListOfParameter(
                        element=EmbeddedDocumentParameter(f.field.document_type)
                    )
                elif isinstance(f.field, ReferenceField):
                    dt = f.field.document_type_obj
                    if dt == "self":
                        dt = self.model
                    self.clean_fields[f.name] = ListOfParameter(
                        element=DocumentParameter(dt, required=f.required)
                    )
            elif isinstance(f, EmbeddedDocumentField):
                self.clean_fields[f.name] = EmbeddedDocumentParameter(f.document_type)
            elif isinstance(f, ReferenceField):
                dt = f.document_type_obj
                if dt == "self":
                    dt = self.model
                self.clean_fields[f.name] = DocumentParameter(dt, required=f.required)
            if f.primary_key:
                self.pk = name
            if name == "uuid":
                self.has_uuid = True
        #
        if not self.query_fields:
            self.query_fields = [
                "%s__%s" % (n, self.query_condition)
                for n, f in self.model._fields.items()
                if f.unique and isinstance(f, StringField)
            ]
        self.unique_fields = [n for n, f in self.model._fields.items() if f.unique]
        # Install JSON API call when necessary
        self.json_collection = self.model._meta.get("json_collection")
        if (
            self.has_uuid
            and hasattr(self.model, "to_json")
            and not hasattr(self, "api_to_json")
            and not hasattr(self, "api_save_json")
            and not hasattr(self, "api_json")
        ):
            self.add_view(
                "api_json",
                self._api_to_json,
                url=r"^(?P<id>[0-9a-f]{24})/json/$",
                method=["GET"],
                access="read",
                api=True,
            )
            self.add_view(
                "api_save_json",
                self._api_save_json,
                url=r"^(?P<id>[0-9a-f]{24})/json/$",
                method=["POST"],
                access="write",
                api=True,
            )
            self.add_view(
                "api_share_info",
                self._api_share_info,
                url=r"^(?P<id>[0-9a-f]{24})/share_info/$",
                method=["GET"],
                access="read",
                api=True,
            )
        if self.json_collection:
            self.bulk_fields += [self._bulk_field_is_builtin]
        # Find field_* and populate custom fields
        self.custom_fields = {}
        for fn in [n for n in dir(self) if n.startswith("field_")]:
            h = getattr(self, fn)
            if callable(h):
                self.custom_fields[fn[6:]] = h

    def get_permissions(self):
        p = super().get_permissions()
        if self.secret_fields:
            p.add("%s:secret" % self.get_app_id().replace(".", ":"))
        return p

    def get_custom_fields(self):
        from noc.main.models.customfield import CustomField

        return list(CustomField.table_fields(self.model._get_collection_name()))

    def get_launch_info(self, request):
        li = super().get_launch_info(request)
        if self.json_collection:
            li["params"]["collection"] = self.json_collection
        cf = self.get_custom_fields()
        if cf:
            li["params"].update(
                {
                    "cust_model_fields": [f.ext_model_field for f in cf],
                    "cust_grid_columns": [f.ext_grid_column for f in cf],
                    "cust_form_fields": [f.ext_form_field for f in cf if not f.is_hidden],
                }
            )
        if self.model:
            li["params"]["protected_field"] = ModelProtectionProfile.get_effective_permissions(
                model_id=get_model_id(self.model), user=request.user
            )
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
        q = reduce(lambda x, y: x | Q(**{get_q(y): query}), qfx[1:], Q(**{qfx[0]: query}))
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
        # Strip ignored fields and convert empty strings to None
        data = {
            str(k): data[k] if data[k] != "" else None
            for k in data
            if k not in self.ignored_fields
            and self.has_field_editable(k)  # Protect individually fields
        }
        # Protect sensitive fields
        if self.secret_fields and not self.has_secret():
            for f in self.secret_fields:
                if f in data:
                    del data[f]
        # Clean up fields
        for f in self.clean_fields:
            if f in data:
                data[f] = self.clean_fields[f].clean(data[f])
        return data

    def cleaned_query(self, q):
        q = q.copy()
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in (
            self.limit_param,
            self.page_param,
            self.start_param,
            self.format_param,
            self.sort_param,
            self.query_param,
            self.only_param,
        ):
            if p in q:
                del q[p]
        # Extract IN
        # extjs not working with same parameter name in query
        for p in list(q.keys()):
            if p.endswith("__in") and self.rx_oper_splitter.match(p):
                field = self.rx_oper_splitter.match(p).group("field") + "__in"
                if field not in q:
                    q[field] = [q[p]]
                else:
                    q[field] += [q[p]]
                del q[p]
        # Normalize parameters
        for p in q:
            if p.endswith("__exists"):
                v = BooleanParameter().clean(q[p])
                q[p] = v
            elif p in self.clean_fields:
                q[p] = self.clean_fields[p].clean(q[p])
        # @todo: correct __ lookups
        if any(p for p in q if p.endswith("__referred")):
            del q[p]
        # builtin
        is_builtin = q.pop("is_builtin", None)
        if self.json_collection and is_builtin in ("true", "false"):
            builtins = [uuid.UUID(x) for x in Collection.get_builtins(self.json_collection)]
            if is_builtin == "true":
                q["uuid__in"] = builtins
            else:
                q["uuid__nin"] = builtins
        return q

    def has_secret(self):
        """
        Check current user has *secret* permission on given app
        :return:
        """
        perm_name = "%s:secret" % (self.get_app_id().replace(".", ":"))
        return perm_name in Permission.get_effective_permissions(get_user())

    def set_file(self, files, o, file_attrs=None):
        """
        Proccessed uploaded file
        :param files:
        :param o:
        :param file_attrs:
        :return:
        """
        return True

    def has_field_editable(self, field):
        return ModelProtectionProfile.has_editable(get_model_id(self.model), get_user(), field)

    def instance_to_dict_list(self, o, fields=None, nocustom=False):
        return self.instance_to_dict(o, fields=fields, nocustom=False)

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = {}
        for n, f in o._fields.items():
            if fields and n not in fields:
                continue
            v = getattr(o, n)
            if v is not None:
                v = f.to_python(v)
            if v is not None:
                if self.secret_fields and n in self.secret_fields and not self.has_secret():
                    # Sensitive fields (limit view only to *secret* permission)
                    v = self.SECRET_MASK
                elif f.name == "bi_id":
                    # Long integer send as string
                    v = str(v)
                elif isinstance(f, GeoPointField):
                    pass
                elif isinstance(f, EnumField):
                    r["%s__label" % f.name] = v.name
                    v = smart_text(v.value)
                elif isinstance(f, ForeignKeyListField):
                    v = [{"label": str(vv.name), "id": vv.id} for vv in v]
                elif isinstance(f, PlainReferenceListField):
                    v = [{"label": str(vv.name), "id": str(vv.id)} for vv in v]
                elif isinstance(f, ForeignKeyField):
                    r["%s__label" % f.name] = smart_text(v)
                    v = v.id
                elif isinstance(f, PlainReferenceField):
                    r["%s__label" % f.name] = smart_text(v)
                    if hasattr(v, "id"):
                        v = str(v.id)
                    else:
                        v = str(v)
                elif isinstance(f, ReferenceField):
                    r["%s__label" % f.name] = smart_text(v)
                    if hasattr(v, "id"):
                        v = str(v.id)
                    else:
                        v = str(v)
                elif f.name in self.field_labels:
                    r[f"{f.name}__label"] = self.field_labels[f.name](v)
                elif (
                    f.name in {"labels", "effective_labels", "default_labels"}
                    and isinstance(f, ListField)
                    and isinstance(f.field, StringField)
                ):
                    # isinstance(f.field, StringField) for exclude pm.scope labels
                    v = sorted(
                        [self.format_label(ll) for ll in Label.from_names(v)],
                        key=lambda x: x["display_order"],
                    )
                elif isinstance(f, (ListField, EmbeddedDocumentListField)):
                    if hasattr(f, "field") and isinstance(f.field, EmbeddedDocumentField):
                        v = [self.instance_to_dict(vv, nocustom=True) for vv in v]
                    elif hasattr(f, "field") and isinstance(f.field, ReferenceField):
                        v = [{"label": str(vv), "id": str(vv.id)} for vv in v]
                    elif hasattr(f, "field") and isinstance(f.field, ObjectIdField):
                        v = [str(vv) for vv in v]
                elif isinstance(f, PlainReferenceListField):
                    v = [{"label": str(vv), "id": str(vv.id)} for vv in v]
                elif isinstance(f, EmbeddedDocumentField):
                    v = self.instance_to_dict(v, nocustom=True)
                elif isinstance(f, BinaryField):
                    v = repr(v)
                elif isinstance(f, DateField):
                    if v:
                        v = v.strftime("%Y-%m-%d")
                    else:
                        v = None
                elif isinstance(f, DynamicField) and isinstance(v, list):
                    v = [str(x) for x in v]
                elif not isinstance(v, (bool, dict, int, str)):
                    if hasattr(v, "id"):
                        v = v.id
                    else:
                        v = smart_text(v)
            elif v is None and isinstance(f, ForeignKeyListField):
                v = []
            r[n] = v
        # Add custom fields
        if not nocustom:
            for f in self.custom_fields:
                r[f] = self.custom_fields[f](o)
        return r

    def instance_to_lookup(self, o, fields=None):
        return {"id": str(o.id), "label": smart_text(o)}

    @view(method=["GET"], url=r"^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict_list)

    @view(method=["GET"], url=r"^lookup/$", access="lookup", api=True)
    def api_lookup(self, request):
        try:
            return self.list_data(request, self.instance_to_lookup)
        except ValueError:
            return self.response(self.lookup_default, status=self.OK)

    @view(method=["GET"], url=r"^tree_lookup/$", access="lookup", api=True)
    def api_lookup_tree(self, request):
        def trim(s):
            return smart_text(s).rsplit(" | ")[-1]

        if not self.parent_field:
            return None
        q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
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
        return {"total": count, "success": True, "data": data}

    @view(method=["POST"], url="^$", access="create", api=True)
    def api_create(self, request):
        is_json = self.site.is_json(request.META.get("CONTENT_TYPE"))
        try:
            attrs = self.clean(
                self.deserialize(request.body) if is_json else self.deserialize_form(request)
            )
        except ValueError as e:
            self.logger.info(
                "Bad request: %r (%s)", request.body if is_json else request.POST.lists(), e
            )
            return self.response(str(e), status=self.BAD_REQUEST)
        if self.pk in attrs:
            del attrs[self.pk]
        if self.has_uuid and not attrs.get("uuid"):
            attrs["uuid"] = uuid.uuid4()
        # Check for duplicates
        if self.unique_fields:
            q = {k: attrs[k] for k in self.unique_fields if k in attrs}
            if q:
                if self.queryset(request).filter(**q).first():
                    return self.response(status=self.CONFLICT)
        o = self.model()
        for k, v in attrs.items():
            if k != self.pk and "__" not in k:
                setattr(o, k, v)
        if request.FILES:
            # Save uploaded file
            try:
                self.set_file(request.FILES, o)
            except ValueError as e:
                return self.response({"message": str(e)}, status=self.BAD_REQUEST)
        try:
            o.save()
        except ValidationError as e:
            return self.response({"message": str(e)}, status=self.BAD_REQUEST)
        except NotUniqueError:
            return self.response(
                {"message": "Duplicate Record (Already exists)"}, status=self.BAD_REQUEST
            )
        # Reread result
        o = self.model.objects.get(**{self.pk: o.pk})
        if request.is_extjs:
            r = {"success": True, "data": self.instance_to_dict(o)}
        else:
            r = self.instance_to_dict(o)
        return self.response(r, status=self.CREATED)

    @view(
        method=["GET"],
        url=r"^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
        access="read",
        api=True,
    )
    def api_read(self, request, id):
        """
        Returns dict with object's fields and values
        """
        qs = self.queryset(request).filter(**{self.pk: id})
        if self.exclude_fields:
            qs = qs.exclude(*self.exclude_fields)
        o = qs.first()
        if not o:
            return HttpResponse("", status=self.NOT_FOUND)
        only = request.GET.get(self.only_param)
        if only:
            only = only.split(",")
        return self.response(self.instance_to_dict(o, fields=only), status=self.OK)

    @view(
        method=["PUT"],
        url=r"^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
        access="update",
        api=True,
    )
    def api_update(self, request, id):
        try:
            attrs = self.clean(self.deserialize(request.body))
        except ValueError as e:
            self.logger.info("Bad request: %r (%s)", request.body, e)
            return self.render_json(
                {"status": False, "message": str(e), "traceback": str(e)},
                status=self.BAD_REQUEST,
            )
        qs = self.queryset(request).filter(**{self.pk: id})
        if self.exclude_fields:
            qs = qs.exclude(*self.exclude_fields)
        o = qs.first()
        if not o:
            return HttpResponse("", status=self.NOT_FOUND)
        if self.has_uuid and not attrs.get("uuid") and not o.uuid:
            attrs["uuid"] = uuid.uuid4()
        # @todo: Check for duplicates
        for k in attrs:
            if not self.has_field_editable(k):
                continue
            if k != self.pk and "__" not in k:
                setattr(o, k, attrs[k])
        try:
            o.save()
        except (ValidationError, ValueError) as e:
            return self.response({"message": str(e)}, status=self.BAD_REQUEST)
        # Reread result
        o = self.model.objects.get(**{self.pk: id})
        if request.is_extjs:
            r = {"success": True, "data": self.instance_to_dict(o)}
        else:
            r = self.instance_to_dict(o)
        return self.response(r, status=self.OK)

    @view(
        method=["DELETE"],
        url=r"^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
        access="delete",
        api=True,
    )
    def api_delete(self, request, id):
        try:
            o = self.queryset(request).get(**{self.pk: id})
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        try:
            o.delete()
        except ValueError as e:
            return self.render_json(
                {"success": False, "message": "ERROR: %s" % e}, status=self.CONFLICT
            )
        return HttpResponse(status=self.DELETED)

    def _api_to_json(self, request, id):
        """
        Expose JSON collection item when available
        """
        o = self.get_object_or_404(self.model, id=id)
        return o.to_json()

    def _api_save_json(self, requiest, id):
        """
        Overwrite json
        """
        o = self.get_object_or_404(self.model, id=id)
        with open(
            os.path.join("collections", self.model._meta["json_collection"], o.get_json_path()), "w"
        ) as fp:
            fp.write(o.to_json())
        return {"status": True}

    def _api_share_info(self, request, id):
        """
        Additional information for JSON sharing process
        :param request:
        :param id:
        :return:
        """
        o = self.get_object_or_404(self.model, id=id)
        coll_name = self.model._meta["json_collection"]
        return {
            "path": os.path.join("collections", coll_name, o.get_json_path()),
            "title": "%s: %s" % (coll_name, str(o)),
            "content": o.to_json(),
            "description": "",
        }

    def _bulk_field_is_builtin(self, data):
        """
        Apply is_builtin field
        :param data:
        :return:
        """
        builtins = Collection.get_builtins(self.json_collection)
        for x in data:
            u = x.get("uuid")
            x["is_builtin"] = u and u in builtins
        return data

    @view(url=r"^actions/group_edit/$", method=["POST"], access="update", api=True)
    def api_action_group_edit(self, request):
        validator = DictParameter(
            attrs={"ids": ListOfParameter(element=DocumentParameter(self.model), convert=True)}
        )
        rv = self.deserialize(request.body)
        try:
            v = validator.clean(rv)
        except InterfaceTypeError as e:
            self.logger.info("Bad request: %r (%s)", request.body, e)
            return self.render_json(
                {"status": False, "message": "Bad request", "traceback": str(e)},
                status=self.BAD_REQUEST,
            )
        objects = v["ids"]
        del v["ids"]
        try:
            v = self.clean(v)
        except ValueError as e:
            return self.render_json(
                {"status": False, "message": "Bad request", "traceback": str(e)},
                status=self.BAD_REQUEST,
            )
        for o in objects:
            for p in v:
                setattr(o, p, v[p])
            o.save()
        return "%d records has been updated" % len(objects)
