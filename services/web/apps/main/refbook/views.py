# ---------------------------------------------------------------------
# main.refbook application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

# NOC modules
from noc.services.web.app.application import Application, view
from noc.aaa.models.permission import Permission
from noc.main.models.refbook import RefBook
from noc.main.models.refbookdata import RefBookData
from noc.core.translation import ugettext as _


class RefBookList(ListView):
    paginate_by = 100

    def get(self, request, *args, **kwargs):
        self._queryset = request._gv_queryset
        self._ctx = request._gv_ctx
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self._queryset

    def get_context_data(self, *args, **kwargs):
        self._ctx.update(super().get_context_data(*args, **kwargs))
        return self._ctx

    def get_template_names(self):
        return self._ctx["app"].get_template_path("view.html")


class RefBookAppplication(Application):
    title = _("Reference Books")

    @view(url=r"^$", url_name="index", menu=[_("Setup"), _("Reference Books")], access="view")
    def view_index(self, request):
        """
        Render list of refbooks
        :param request:
        :return:
        """
        ref_books = RefBook.objects.filter(is_enabled=True).order_by("name")
        return self.render(request, "index.html", ref_books=ref_books)

    @view(url=r"^(?P<refbook_id>\d+)/$", url_name="view", access="view")
    def view_view(self, request, refbook_id):
        """
        Refbook preview
        :param request:
        :param refbook_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        can_edit = not rb.is_builtin and Permission.has_perm(
            request.user, "main.change_refbookdata"
        )
        queryset = rb.refbookdata_set.all()
        # Search
        if request.GET and "query" in request.GET and request.GET["query"]:
            query = request.GET["query"]
            # Build query clause
            w = []
            p = []
            for f in rb.refbookfield_set.filter(search_method__isnull=False):
                x = f.get_extra(query)
                if not x:
                    continue
                w += x["where"]
                p += x["params"]
            w = " OR ".join(["(%s)" % xx for xx in w])
            queryset = queryset.extra(where=["(%s)" % w], params=p)
        else:
            query = ""
        # Use generic view for final result
        request._gv_queryset = queryset
        request._gv_ctx = {"rb": rb, "can_edit": can_edit, "query": query, "app": self}
        return RefBookList().get(request)

    @view(url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/$", url_name="item", access="view")
    def view_item(self, request, refbook_id, record_id):
        """
        Item preview
        :param request:
        :param refbook_id:
        :param record_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        rbr = get_object_or_404(RefBookData, id=int(record_id), ref_book=rb)
        can_edit = not rb.is_builtin and Permission.has_perm(
            request.user, "main.change_refbookdata"
        )
        return self.render(request, "item.html", {"rb": rb, "record": rbr, "can_edit": can_edit})

    @view(url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/edit/$", url_name="edit", access="change")
    def view_edit(self, request, refbook_id, record_id=0):
        """
        Edit item
        :param request:
        :param refbook_id:
        :param record_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        rbr = get_object_or_404(RefBookData, id=int(record_id), ref_book=rb)
        can_edit = not rb.is_builtin and Permission.has_perm(
            request.user, "main.change_refbookdata"
        )
        if not can_edit:
            return self.response_forbidden("Read-only refbook")
        if request.POST:  # Edit refbook
            if not can_edit:
                return self.response_forbidden("Read-only refbook")
            # Retrieve record data
            fns = [int(k[6:]) for k in request.POST if k.startswith("field_")]
            data = ["" for i in range(max(fns) + 1)]
            for i in fns:
                data[i] = request.POST["field_%d" % i]
            rbr.value = data
            rbr.save()
            self.message_user(request, "Record updated successfully")
            return self.response_redirect("main:refbook:item", rb.id, rbr.id)
        return self.render(request, "edit.html", {"rb": rb, "record": rbr})

    @view(
        url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/delete/$", url_name="delete", access="delete"
    )
    def view_delete(self, request, refbook_id, record_id):
        """
        Delete refbook record
        :param request:
        :param refbook_id:
        :param record_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        can_edit = not rb.is_builtin and Permission.has_perm(
            request.user, "main.change_refbookdata"
        )
        if not can_edit:
            return self.response_forbidden()
        rbd = get_object_or_404(RefBookData, ref_book=rb, id=int(record_id))
        rbd.delete()
        self.message_user(request, "Record deleted")
        return self.response_redirect("main:refbook:view", rb.id)

    @view(url=r"^(?P<refbook_id>\d+)/new/$", url_name="new", access="add")
    def view_new(self, request, refbook_id):
        """
        Create refbook record
        :param request:
        :param refbook_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        can_edit = not rb.is_builtin and Permission.has_perm(
            request.user, "main.change_refbookdata"
        )
        if not can_edit:
            return self.response_forbidden("Read-only refbook")
        if request.POST:  # Edit refbook
            if not can_edit:
                return self.response_forbidden("Read-only refbook")
            # Retrieve record data
            fns = [int(k[6:]) for k in request.POST if k.startswith("field_")]
            data = ["" for i in range(max(fns) + 1)]
            for i in fns:
                data[i] = request.POST["field_%d" % i]
            rbr = RefBookData(ref_book=rb, value=data)
            rbr.save()
            self.message_user(request, "Record added")
            return self.response_redirect("main:refbook:item", rb.id, rbr.id)
        return self.render(request, "new.html", {"rb": rb})
