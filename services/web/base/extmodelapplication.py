# ----------------------------------------------------------------------
# ExtModelApplication implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import os
import uuid
from collections import defaultdict
from functools import reduce

# Third-party modules
from django.http import HttpResponse
from django.db.models.fields import (
    CharField,
    BooleanField,
    IntegerField,
    FloatField,
    DateField,
    DateTimeField,
    related,
)
from django.db.models import Q
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.sa.interfaces.base import (
    BooleanParameter,
    IntParameter,
    FloatParameter,
    TagsParameter,
    NoneParameter,
    StringListParameter,
    DictParameter,
    ListOfParameter,
    ModelParameter,
    InterfaceTypeError,
)
from noc.core.validators import is_int
from noc.models import is_document
from noc.core.stencil import stencil_registry
from noc.core.debug import error_report
from noc.aaa.models.permission import Permission
from noc.aaa.models.modelprotectionprofile import ModelProtectionProfile
from noc.main.models.label import Label
from noc.core.middleware.tls import get_user
from noc.core.comp import smart_text
from noc.core.collection.base import Collection
from noc.models import get_model_id
from noc.core.model.util import is_related_field
from noc.inv.models.resourcegroup import ResourceGroup
from .extapplication import ExtApplication, view
from .interfaces import DateParameter, DateTimeParameter


class ExtModelApplication(ExtApplication):
    model = None  # Django model to expose
    icon = "icon_application_view_list"
    query_fields = []  # Use all unique fields by default
    query_condition = "startswith"  # Match method for string fields
    int_query_fields = []  # Query integer fields for exact match
    pk_field_name = None  # Set by constructor
    clean_fields = {"id": IntParameter()}  # field name -> Parameter instance
    custom_fields = {}  # name -> handler, populated automatically
    # m2m fields
    custom_m2m_fields = {}  # Name -> Model
    secret_fields = (
        None  # Set of sensitive fields. "secret" permission is required to show of modify
    )
    order_map = {}  # field name -> SQL query for ordering
    lookup_default = [{"id": "Leave unchanged", "label": "Leave unchanged"}]
    ignored_fields = {"id", "bi_id", "state"}
    SECRET_MASK = "********"
    file_fields_mask = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_table = self.model._meta.db_table
        self.pk_field_name = self.model._meta.pk.name
        self.pk = self.pk_field_name
        self.has_uuid = False
        # Prepare field converters
        self.clean_fields = self.clean_fields.copy()  # name -> Parameter
        self.fk_fields = {}
        self.field_defaults = {}
        for f in self.model._meta.fields:
            if f.name in self.clean_fields:
                continue  # Overriden behavior
            vf = self.get_validator(f)
            if vf:
                if f.null:
                    vf = NoneParameter() | vf
                self.clean_fields[f.name] = vf
            if f.default is not None and not f.blank:
                self.field_defaults[f.name] = f.default
            if f.name == "uuid":
                self.has_uuid = True
        # m2m fields
        self.m2m_fields = {}  # Name -> Model
        if self.custom_m2m_fields:
            self.m2m_fields.update(self.custom_m2m_fields)
        for f in self.model._meta.many_to_many:
            self.m2m_fields[f.name] = f.remote_field.model
        # Find field_* and populate custom fields
        self.custom_fields = {}
        for fn in [n for n in dir(self) if n.startswith("field_")]:
            h = getattr(self, fn)
            if callable(h):
                self.custom_fields[fn[6:]] = h
        #
        if not self.query_fields:
            # By default - search in unique text fields
            self.query_fields = [
                "%s__%s" % (f.name, self.query_condition)
                for f in self.model._meta.fields
                if f.unique and isinstance(f, CharField)
            ]
        # Add searchable custom fields
        self.query_fields += [
            "%s__%s" % (f.name, self.query_condition)
            for f in self.get_custom_fields()
            if f.is_searchable
        ]
        # Install JSON API call when necessary
        if hasattr(self.model, "_json_collection"):
            self.json_collection = self.model._json_collection["json_collection"]
        else:
            self.json_collection = None
        if (
            self.has_uuid
            and hasattr(self.model, "to_json")
            and not hasattr(self, "api_to_json")
            and not hasattr(self, "api_json")
        ):
            self.add_view(
                "api_json",
                self._api_to_json,
                url=r"^(?P<id>\d+)/json/$",
                method=["GET"],
                access="read",
                api=True,
            )
            self.add_view(
                "api_share_info",
                self._api_share_info,
                url=r"^(?P<id>\d+)/share_info/$",
                method=["GET"],
                access="read",
                api=True,
            )
        if self.json_collection:
            self.bulk_fields += [self._bulk_field_is_builtin]

    def get_permissions(self):
        p = super().get_permissions()
        if self.secret_fields:
            p.add("%s:secret" % self.get_app_id().replace(".", ":"))
        return p

    def get_validator(self, field):
        """
        Returns Parameter instance or None to clean up field
        :param field:
        :type field: Field
        :return:
        """
        from noc.core.model.fields import TagsField, TextArrayField

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
            self.fk_fields[field.name] = field.remote_field.model
            return ModelParameter(field.remote_field.model, required=not field.null)
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
        li = super().get_launch_info(request)
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
            if "__" not in f:
                return "%s__%s" % (f, self.query_condition)
            else:
                return f

        q = reduce(
            lambda x, y: x | Q(**{get_q(y): query}),
            self.query_fields[1:],
            Q(**{get_q(self.query_fields[0]): query}),
        )
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
        # Set defaults
        for f in data:
            if data[f] is None and f in self.field_defaults:
                v = self.field_defaults[f]
                if callable(v):
                    v = v()
                data[f] = v
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
        return data

    def cleaned_query(self, q):
        nq = {}
        q = q.copy()
        # Extract IN
        # extjs not working with same parameter name in query
        for p in list(q.keys()):
            if p.endswith(self.in_param):
                match = self.rx_oper_splitter.match(p)
                if match:
                    field = self.rx_oper_splitter.match(p).group("field") + self.in_param
                    if field not in q:
                        q[field] = "%s" % (q[p])
                    else:
                        q[field] += ",%s" % (q[p])
                    del q[p]
        for p in q:
            if p.endswith("__exists"):
                v = BooleanParameter().clean(q[p])
                nq[p.replace("__exists", "__isnull")] = not v
                continue
            if "__" in p:
                np, lt = p.split("__", 1)
            else:
                np, lt = p, None
                # Skip ignored params
            if np in self.ignored_params or p in (
                self.limit_param,
                self.page_param,
                self.start_param,
                self.format_param,
                self.sort_param,
                self.group_param,
                self.query_param,
                self.only_param,
            ):
                continue
            v = q[p]
            if self.in_param in p and isinstance(v, str):
                v = v.split(",")
            if v == "\x00":
                v = None
            # Pass through interface cleaners
            if lt == "referred":
                # Unroll __referred
                app, fn = v.split("__", 1)
                model = getattr(self.site.apps[app], "model", None)
                if model and not is_document(model):
                    extra_where = '%s."%s" IN (SELECT "%s" FROM %s)' % (
                        self.model._meta.db_table,
                        self.model._meta.pk.name,
                        model._meta.get_field(fn).attname,
                        model._meta.db_table,
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
            elif np in {"effective_service_groups", "effective_client_groups"} and v:
                nq[f"{np}__overlap"] = ResourceGroup.get_nested_ids(v)
                continue
            elif np in self.fk_fields and lt:
                # dereference
                try:
                    nq[np] = self.fk_fields[np].objects.get(**{lt: v})
                except self.fk_fields[np].DoesNotExist:
                    nq[np] = 0  # False search
                continue
            elif np in self.clean_fields and self.in_param in p:
                v = ListOfParameter(self.clean_fields[np]).clean(v)
            elif np in self.clean_fields:  # @todo: Check for valid lookup types
                v = self.clean_fields[np].clean(v)
                # Write back
            nq[p] = v
        return nq

    def has_secret(self):
        """
        Check current user has *secret* permission on given app
        :return:
        """
        perm_name = "%s:secret" % (self.get_app_id().replace(".", ":"))
        return perm_name in Permission.get_effective_permissions(get_user())

    def has_field_editable(self, field):
        return ModelProtectionProfile.has_editable(get_model_id(self.model), get_user(), field)

    def instance_to_dict(self, o, fields=None):
        r = {}
        for f in o._meta.local_fields:
            if fields and f.name not in fields:
                continue  # Restrict to selected fields
            if (
                self.secret_fields
                and f.name in self.secret_fields
                and getattr(o, f.name)
                and not self.has_secret()
            ):
                # Sensitive fields (limit view only to *secret* permission)
                r[f.name] = self.SECRET_MASK
            elif f.name == "bi_id":
                # Long integer send as string
                r[f.name] = str(o.bi_id)
            elif f.name == "tags":
                # Send tags as a list
                r[f.name] = getattr(o, f.name)
            elif f.name == "shape":
                if o.shape:
                    v = stencil_registry.get(o.shape)
                    r[f.name] = v.id
                    r["%s__label" % f.name] = smart_text(v.title)
            elif f.name in {"labels", "effective_labels"} and isinstance(f, ArrayField):
                r[f.name] = sorted(
                    [self.format_label(ll) for ll in Label.from_names(getattr(o, f.name, []))],
                    key=lambda x: x["display_order"],
                )
            elif hasattr(f, "document"):
                # DocumentReferenceField
                v = getattr(o, f.name)
                if v:
                    r[f.name] = str(v.pk)
                    r["%s__label" % f.name] = smart_text(v)
                else:
                    r[f.name] = None
                    r["%s__label" % f.name] = ""
            elif not is_related_field(f):
                v = f.value_from_object(o)
                if (
                    v is not None
                    and not isinstance(v, str)
                    and not isinstance(v, int)
                    and not isinstance(v, (bool, list))
                ):
                    if isinstance(v, datetime.datetime):
                        v = v.isoformat()
                    else:
                        v = smart_text(v)
                r[f.name] = v
            else:
                v = getattr(o, f.name)
                if v:
                    r[f.name] = v._get_pk_val()
                    r["%s__label" % f.name] = smart_text(v)
                else:
                    r[f.name] = None
                    r["%s__label" % f.name] = ""
        # Add m2m fields
        for n in self.m2m_fields:
            r[n] = [{"id": str(mmo.pk), "label": smart_text(mmo)} for mmo in getattr(o, n).all()]
            # r[n] = list(getattr(o, n).values_list("id", flat=True))
        # Add custom fields
        for f in self.custom_fields:
            if fields and f not in fields:
                continue
            r[f] = self.custom_fields[f](o)
        return r

    def instance_to_lookup(self, o, fields=None):
        return {"id": o.id, "label": smart_text(o)}

    def lookup_tags(self, q, name, value):
        if not value:
            return
        if isinstance(value, str):
            value = [value]
        tq = ("%%s::text[] <@ %s.tags" % self.db_table, [value])
        if None in q:
            q[None] += [tq]
        else:
            q[None] = [tq]

    def lookup_labels(self, q, name, value):
        if not value:
            return
        if isinstance(value, str):
            value = [value]
        q[f"{name}__contains"] = value

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

    def update_file(self, files, o, file_attrs=None):
        """
        Proccessed uploaded file
        :param files:
        :param o:
        :param file_attrs:
        :return:
        """
        return True

    def split_file(self, pdata):
        """
        Split post data to (fields, file_fields) data
        """
        if self.file_fields_mask:
            fdata = defaultdict(dict)
            for f in list(pdata):
                match = self.file_fields_mask.match(f)
                if match:
                    fdata[match.group("findex")][match.group("fname")] = pdata[f]
                    del pdata[f]
            return pdata, fdata
        return pdata, {}

    def extra_query(self, q, order):
        new_order = []
        extra_select = {}
        for n, o in enumerate(order):
            direction = ""
            if o.startswith("-"):
                fname = o[1:]
                direction = "-"
            else:
                fname = o
            if o in self.order_map:
                no = f"{fname}_order_{n}"
                extra_select[no] = self.order_map[o]
                new_order += [f"{direction}{no}"]
            else:
                new_order += [o]
        extra = {}
        if extra_select:
            extra["select"] = extra_select
        return extra, new_order

    def can_create(self, user, obj):
        """
        Check user can create object. Used to additional
        restrictions after permissions check
        :param user:
        :param obj: Object instance
        :return: True if access granted
        """
        return True

    def can_update(self, user, obj):
        """
        Check user can update object. Used to additional
        restrictions after permissions check
        :param user:
        :param obj: Object instance
        :return: True if access granted
        """
        return True

    def can_delete(self, user, obj):
        """
        Check user can delete object. Used to additional
        restrictions after permissions check
        :param user:
        :param obj: Object instance
        :return: True if access granted
        """
        return True

    def instance_to_dict_list(self, o, fields=None):
        return self.instance_to_dict(o, fields=fields)

    @view(method=["GET"], url=r"^$", access="read", api=True)
    def api_list(self, request):
        try:
            return self.list_data(request, self.instance_to_dict_list)
        except Exception as e:
            error_report()
            return self.response({"status": False, "message": str(e)}, status=self.INTERNAL_ERROR)

    @view(method=["GET"], url=r"^lookup/$", access="lookup", api=True)
    def api_lookup(self, request):
        try:
            return self.list_data(request, self.instance_to_lookup)
        except ValueError:
            return self.response(self.lookup_default, status=self.OK)
        except Exception as e:
            error_report()
            return self.response({"status": False, "message": str(e)}, status=self.INTERNAL_ERROR)

    @view(method=["POST"], url=r"^$", access="create", api=True)
    def api_create(self, request):
        if self.site.is_json(request.META.get("CONTENT_TYPE")):
            attrs, m2m_attrs = self.split_mtm(self.deserialize(request.body))
        else:
            attrs, m2m_attrs = self.split_mtm(self.deserialize_form(request))
        attrs, file_attrs = self.split_file(attrs)
        try:
            attrs = self.clean(attrs)
        except ValueError as e:
            self.logger.info(
                "Bad request: %r (%s)", request.body if not request._read_started else request, e
            )
            return self.render_json(
                {"success": False, "message": "Bad request", "traceback": str(e)},
                status=self.BAD_REQUEST,
            )
        if self.has_uuid and not attrs.get("uuid"):
            attrs["uuid"] = uuid.uuid4()
        try:
            # Exclude callable values from query
            # (Django raises exception on pyRules)
            # @todo: Check unique fields only?
            qattrs = {k: attrs[k] for k in attrs if not callable(attrs[k])}
            # Check for duplicates
            self.queryset(request).get(**qattrs)
            return self.render_json(
                {"success": False, "message": "Duplicated record"}, status=self.CONFLICT
            )
        except self.model.MultipleObjectsReturned:
            return self.render_json(
                {"status": False, "message": "Duplicated record"}, status=self.CONFLICT
            )
        except self.model.DoesNotExist:
            o = self.model(**attrs)
            # Run models validators
            try:
                o.full_clean(exclude=list(self.ignored_fields))
            except ValidationError as e:
                e_msg = []
                for f in e.message_dict:
                    e_msg += ["%s: %s" % (f, "; ".join(e.message_dict[f]))]
                return self.render_json(
                    {"status": False, "message": "Validation error: %s" % " | ".join(e_msg)},
                    status=self.BAD_REQUEST,
                )
            # Check permissions
            if not self.can_create(request.user, o):
                return self.render_json(
                    {"status": False, "message": "Permission denied"}, status=self.FORBIDDEN
                )
            # Check for duplicates
            try:
                o.save()
                if m2m_attrs:
                    self.update_m2ms(o, m2m_attrs)
                if file_attrs:
                    # Save uploaded file
                    self.update_file(request.FILES, o, file_attrs)
            except IntegrityError as e:
                return self.render_json(
                    {"status": False, "message": "Integrity error: %s" % e}, status=self.CONFLICT
                )
            # Check format
            if request.is_extjs:
                rs = {"success": True, "data": self.instance_to_dict(o)}
            else:
                rs = self.instance_to_dict(o)
            return self.response(rs, status=self.CREATED)

    @view(method=["GET"], url=r"^(?P<id>\d+)/?$", access="read", api=True)
    def api_read(self, request, id):
        """
        Returns dict with object's fields and values
        """
        try:
            o = self.queryset(request).get(**{self.pk: int(id)})
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        only = request.GET.get(self.only_param)
        if only:
            only = only.split(",")
        try:
            return self.response(self.instance_to_dict(o, fields=only), status=self.OK)
        except Exception as e:
            error_report()
            return self.response({"status": False, "message": str(e)}, status=self.INTERNAL_ERROR)

    @view(method=["PUT"], url=r"^(?P<id>\d+)/?$", access="update", api=True)
    def api_update(self, request, id):
        if self.site.is_json(request.META.get("CONTENT_TYPE")):
            attrs, m2m_attrs = self.split_mtm(self.deserialize(request.body))
        else:
            attrs, m2m_attrs = self.split_mtm(self.deserialize_form(request))
        attrs, file_attrs = self.split_file(attrs)
        try:
            attrs = self.clean(attrs)
        except ValueError as e:
            self.logger.info(
                "Bad request: %r (%s)", request.body if not request._read_started else request, e
            )
            return self.render_json(
                {"success": False, "message": "Bad request", "traceback": str(e)},
                status=self.BAD_REQUEST,
            )
        except Exception as e:
            error_report()
            return self.response({"status": False, "message": str(e)}, status=self.INTERNAL_ERROR)
        # Find object
        try:
            o = self.queryset(request).get(**{self.pk: int(id)})
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        # Update attributes
        for k, v in attrs.items():
            if (
                self.secret_fields
                and k in self.secret_fields
                and not self.has_secret()
                and self.has_field_editable(k)
            ):
                continue
            setattr(o, k, v)
        # Run models validators
        try:
            o.clean_fields()
        except ValidationError as e:
            e_msg = []
            for f in e.message_dict:
                e_msg += ["%s: %s" % (f, "; ".join(e.message_dict[f]))]
            return self.render_json(
                {"status": False, "message": "Validation error: %s" % " | ".join(e_msg)},
                status=self.BAD_REQUEST,
            )
        # Check permissions
        if not self.can_create(request.user, o):
            return self.render_json(
                {"status": False, "message": "Permission denied"}, status=self.FORBIDDEN
            )
        # Save
        try:
            o.save()
            if m2m_attrs:
                self.update_m2ms(o, m2m_attrs)
            if file_attrs:
                # Save uploaded file
                self.update_file(request.FILES, o, file_attrs)
        except IntegrityError as e:
            return self.render_json(
                {"success": False, "message": f"Integrity error {str(e)}"}, status=self.CONFLICT
            )
        except (ValidationError, ValueError) as e:
            return self.response({"success": False, "message": str(e)}, status=self.BAD_REQUEST)
        except Exception as e:
            error_report()
            return self.response({"status": False, "message": str(e)}, status=self.INTERNAL_ERROR)
        if request.is_extjs:
            r = {"success": True, "data": self.instance_to_dict(o)}
        else:
            r = self.instance_to_dict(o)
        return self.response(r, status=self.OK)

    @view(method=["DELETE"], url=r"^(?P<id>\d+)/?$", access="delete", api=True)
    def api_delete(self, request, id):
        try:
            o = self.queryset(request).get(**{self.pk: int(id)})
        except self.model.DoesNotExist:
            return self.render_json(
                {"status": False, "message": "Not found"}, status=self.NOT_FOUND
            )
        # Check permissions
        if not self.can_delete(request.user, o):
            return self.render_json(
                {"status": False, "message": "Permission denied"}, status=self.FORBIDDEN
            )
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

    def _api_share_info(self, request, id):
        """
        Additional information for JSON sharing process
        :param request:
        :param id:
        :return:
        """
        o = self.get_object_or_404(self.model, id=id)
        coll_name = self.model._json_collection["json_collection"]
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
            attrs={"ids": ListOfParameter(element=ModelParameter(self.model), convert=True)}
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
