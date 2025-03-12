# ---------------------------------------------------------------------
# SimpleReport implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import csv
import decimal
import pprint
from functools import reduce
from io import StringIO

# Third-party modules
from django.utils.dateformat import DateFormat

# NOC modules
from noc.core.translation import ugettext as _
from noc.config import config
from noc.core.html import tags_list
from noc.core.comp import smart_text
from .reportapplication import ReportApplication


INDENT = "    "


class ReportNode(object):
    """
    Abstract Report Node
    """

    tag = None

    def __init__(self, name=None):
        self.name = name

    def quote(self, s):
        """
        Return XML-quoted value
        """
        return (
            smart_text(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def format_opening_xml_tag(self, **kwargs):
        """
        Return opening XML tag
        """
        s = "<%s" % self.tag
        for k, v in kwargs.items():
            if v:
                s += " %s='%s'" % (k, self.quote(v))
        s += ">"
        return s

    def format_closing_xml_tag(self):
        """
        Return closing XML tag
        """
        return "</%s>" % self.tag

    def indent(self, s, n=1):
        """
        Indent block of code
        """
        i = INDENT * n
        return i + s.replace("\n", "\n" + i)

    def to_xml(self):
        """
        Return XML presentation of Node
        """
        return ""

    def to_html(self, **kwargs):
        """
        Return HTML presentation of Node
        """
        return ""

    def to_csv(self, delimiter=","):
        """
        Return CSV presentation of Node
        """
        return ""


class Report(ReportNode):
    """
    Report root node
    """

    tag = "report"

    def __init__(self, name=None):
        super().__init__(name=name)
        self.sections = []  # Must be ReportSection instances

    def append_section(self, s):
        self.sections += [s]

    def to_xml(self):
        """
        Return XML code for report
        :return:
        """
        s = [self.format_opening_xml_tag(name=self.name)]
        s += [self.indent("<sections>")]
        s += [self.indent(x.to_xml(), 2) for x in self.sections]
        s += [self.indent("</sections>")]
        s += [self.format_closing_xml_tag()]
        return "\n".join(s)

    def to_html(self, include_buttons=True, **kwargs):
        """
        Return HTML code for report
        :return:
        """
        return "\n".join([s.to_html(include_buttons=include_buttons) for s in self.sections])

    def to_csv(self, delimiter=","):
        """
        Return CSV for report
        :return:
        """
        return "\n".join([x for x in [s.to_csv(delimiter=delimiter) for s in self.sections] if x])


class ReportSection(ReportNode):
    """
    Abstract class for report sections
    """


class TextSection(ReportSection):
    """
    Section containing text. Consists of title and text
    text bay be string or list of paragraphs.
    Skipped in CSV mode
    """

    tag = "text"

    def __init__(self, name=None, title=None, text=None):
        super().__init__(name=name)
        self.title = title
        self.text = text  # Either string o list of strings

    @property
    def paragraphs(self):
        """
        Returns a list of paragraphs
        """
        if not self.text:
            return []
        if isinstance(self.text, str):
            return [self.text]
        else:
            return self.text

    def to_xml(self):
        """
        Return XML presentation of text section
        """
        s = [self.format_opening_xml_tag(name=self.name, title=self.title)]
        s += [self.indent("<par>%s</par>" % self.quote(p)) for p in self.paragraphs]
        s += [self.format_closing_xml_tag()]
        return "\n".join(s)

    def to_html(self, include_buttons=True):
        """
        Return HTML presentation of text section
        """
        s = []
        if self.title:
            s += ["<h2>%s</h2>" % self.quote(self.title)]
        s += ["<p>%s</p>" % self.quote(p) for p in self.paragraphs]
        return "\n".join(s)


#
# Precomputed size multipliers
# List of (limit, divider, suffix)
#
SIZE_DATA = []
dec = decimal.Decimal(1024)
for suffix in ["KB", "MB", "GB", "TB", "PB"]:
    SIZE_DATA += [(dec * 1024, dec, suffix)]
    dec *= 1024


class SafeString(str):
    """
    Do not perform HTML quoting
    """


class TableColumn(ReportNode):
    """
    Table column.
    Contains rules for formatting the cells
    """

    tag = "column"
    ALIGN_LEFT = 1
    ALIGN_RIGHT = 2
    ALIGN_CENTER = 3
    H_ALIGN_MASK = 3

    def __init__(self, name, title=None, align=None, format=None, total=None, total_label=None):
        super().__init__(name=name)
        # self.name = name
        self.title = title if title else name
        self.align = (
            {
                "l": self.ALIGN_LEFT,
                "left": self.ALIGN_LEFT,
                "r": self.ALIGN_RIGHT,
                "right": self.ALIGN_RIGHT,
                "c": self.ALIGN_CENTER,
                "center": self.ALIGN_CENTER,
            }[align.lower()]
            if align
            else None
        )
        self.format = getattr(self, "f_%s" % format) if isinstance(format, str) else format
        self.total = getattr(self, "ft_%s" % total) if isinstance(total, str) else total
        self.total_label = total_label
        self.total_data = []
        self.subtotal_data = []

    @property
    def has_total(self):
        """
        Check column has total
        :return:
        """
        return self.total

    def start_section(self):
        """
        Reset sub-totals
        :return:
        """
        self.subtotal_data = []

    def contribute_data(self, s):
        """
        Contribute data to totals
        :param s:
        :return:
        """
        if self.total:
            self.total_data += [s]

    def format_data(self, s):
        """
        Return formatted cell
        :param s:
        :return:
        """
        if s is None or s == "":
            return ""
        elif not self.format:
            return s
        else:
            return self.format(s)

    def to_xml(self):
        """
        Return XML representation of column
        :return:
        """
        return (
            self.format_opening_xml_tag(name=self.name, align=self.align)
            + self.quote(self.title)
            + self.format_closing_xml_tag()
        )

    def html_td_attrs(self):
        """
        Return quoted HTML TD attributes
        :return:
        """
        attrs = {}
        if self.align:
            if self.align & self.H_ALIGN_MASK == self.ALIGN_LEFT:
                attrs["align"] = "left"
            elif self.align & self.H_ALIGN_MASK == self.ALIGN_RIGHT:
                attrs["align"] = "right"
            elif self.align & self.H_ALIGN_MASK == self.ALIGN_CENTER:
                attrs["align"] = "center"
        return " " + " ".join(["%s='%s'" % (k, self.quote(v)) for k, v in attrs.items()])

    def format_html(self, s):
        """
        Render single cell
        :param s:
        :return:
        """
        d = self.format_data(s)
        if not isinstance(d, SafeString):
            d = self.quote(d)
        return "<td%s>%s</td>" % (self.html_td_attrs(), d)

    def format_html_total(self):
        """
        Render totals
        :return:
        """
        if self.total:
            total = self.format_data(self.total(self.total_data))
        elif self.total_label:
            total = self.total_label
        else:
            total = ""
        return "<td%s><b>%s</b></td>" % (self.html_td_attrs(), total)

    def format_html_subtotal(self, d):
        """
        Render subtotals
        :param d:
        :return:
        """
        if self.total:
            total = self.format_data(self.total(d))
        elif self.total_label:
            total = self.total_label
        else:
            total = ""
        return "<td%s><b>%s</b></td>" % (self.html_td_attrs(), total)

    def f_date(self, f):
        """
        Display date according to settings
        :param f:
        :return:
        """
        return DateFormat(f).format(config.date_time_formats.date_format)

    def f_time(self, f):
        """
        Display time according to settings
        :param f:
        :return:
        """
        return DateFormat(f).format(config.date_time_formats.time_format)

    def f_datetime(self, f):
        """
        Display date and time according to settings
        :param f:
        :return:
        """
        return DateFormat(f).format(config.date_time_formats.datetime_format)

    def f_size(self, f):
        """
        Display pretty size
        :param f:
        :return:
        """
        f = decimal.Decimal(f)
        for limit, divider, suffix in SIZE_DATA:
            if f < limit:
                return ("%8.2f%s" % (f / divider, suffix)).strip()
        limit, divider, suffix = SIZE_DATA[-1]
        return ("%8.2f%s" % (f / divider, suffix)).strip()

    def f_numeric(self, f):
        """
        Display pretty numeric
        :param f:
        :return:
        """
        if not f:
            return "0"
        if isinstance(f, float):
            f = str(f)
        try:
            f = decimal.Decimal(f)
        except decimal.InvalidOperation:
            return "-"
        sign, digits, exp = f.as_tuple()
        if exp:
            r = "." + "".join(map(str, digits[exp:]))
            if r == ".0":
                r = ""
            digits = digits[:exp]
        else:
            r = ""
        while digits:
            r = " " + "".join(map(str, digits[-3:])) + r
            digits = digits[:-3]
        r = r.strip()
        if sign:
            r = "-" + r
        return r

    def f_bool(self, f):
        """
        Display boolean field
        """
        if f:
            return SafeString("<i class='fa fa-check' style='color:#2ecc71'></i>")
        else:
            return SafeString("<i class='fa fa-times' style='color:#c0392b'></i>")

    def f_url(self, url):
        """
        Display url field
        """
        return SafeString('<a href="%s", target="_blank">Link</a>' % url)

    def f_integer(self, f):
        """
        Display pretty-formatted integer
        """
        return self.f_numeric(int(f))

    def f_percent(self, f):
        """
        Display numeric with % sign
        """
        return self.f_numeric(f) + "%"

    def f_pprint(self, f):
        """
        Returns a pretty-printed object
        """
        return SafeString("<pre>%s</pre>" % pprint.pformat(f))

    def f_string(self, f):
        """
        Returns a pretty-printed object
        """
        return str(f)

    def f_tags(self, f):
        """
        Display and object's tags
        """
        try:
            return SafeString(tags_list(f))
        except Exception:
            return ""

    def ft_sum(self, f):
        """
        Returns a sum of not-null elements
        """
        return reduce(lambda x, y: x + y, [decimal.Decimal(str(z)) for z in f if z], 0)

    def ft_count(self, f):
        """
        Returns a count of not-null elements
        """
        return len([x for x in f if x])


class SectionRow(object):
    """
    Delimiter row
    """

    def __init__(self, name, title=None, subtotal=True):
        self.name = name
        self.title = title if title else name
        self.subtotal = subtotal
        self.data = {}

    def contribute_data(self, column, d):
        if self.subtotal:
            try:
                self.data[column] += [d]
            except KeyError:
                self.data[column] = [d]


#
# Section containing table
#
#
class TableSection(ReportSection):
    tag = "table"

    def __init__(self, name=None, columns=None, enumerate=False, data=None):
        super().__init__(name=name)
        self.columns = []
        for c in columns or []:
            if isinstance(c, str) or hasattr(c, "__unicode__"):
                self.columns += [TableColumn(smart_text(c))]
            else:
                self.columns += [c]
        self.data = data or []
        self.enumerate = enumerate
        self.has_total = reduce(
            lambda x, y: x or y, [c.has_total for c in self.columns], False
        )  # Check werether table has totals

    def to_xml(self):
        """
        Return XML representation of table
        """
        s = [self.format_opening_xml_tag(name=self.name)]
        s += [self.indent("<columns>")]
        s += [self.indent(c.to_xml(), 2) for c in self.columns]
        s += [self.indent("</columns>")]
        s += [self.format_closing_xml_tag()]
        return "\n".join(s)

    def to_html(self, include_buttons=True):
        """
        Return HTML representation of table
        :return:
        """

        def render_subtotals():
            if not current_section.data:
                return []
            s = ["<tr style='font-style:italic;background-color:#C0C0C0'>"]
            if self.enumerate:
                s += ["<td></td>"]
            s += [c.format_html_subtotal(current_section.data[c]) for c in self.columns]
            s += ["</tr>"]
            return s

        if include_buttons:
            s = [
                "<script type='text/javascript' src='/ui/pkg/jquery.table2csv/jquery.table2csv.js'></script>",
                "<form id='report'>",
                "<input type='hidden' name='content_type' value='text/csv; charset=utf8'>",
                "<input type='hidden' name='filename' value='report.csv'>",
                "<input type='hidden' name='data' id='csv_data'>",
                "<input class='button' disabled type='button' value='CSV' onclick='getData(\".report-table\", \",\");'>",
                "<input class='button' disabled type='button' value='"
                + _("Print")
                + "'onclick='window.print()'>",
                "<input class='button' disabled type='button' value='PDF' onclick='getPDFReport(\".report-table\")'>",
                "<input class='button' disabled type='button' value='SSV' onclick='getData(\".report-table\", \";\");'>",
                "</form>",
                "<script>",
                "function getData(t, delimiter) {",
                "  $('.button').attr('disabled','disabled');",
                "  setTimeout(function() {",
                "      var v = $(t).TableCSVExport({delivery: 'value', separator: delimiter});",
                "      $('#csv_data').val(v);",
                "      $('.button').prop('disabled', false);",
                "      $('#report').submit();",
                "  }, 0);",
                "}",
                "function getPDFReport(t) {",
                "  $('.button').attr('disabled','disabled');",
                "  setTimeout(function() {",
                "      getPDF(t)",
                "      $('.button').prop('disabled', false);",
                "  }, 0);",
                "}",
                "$( document ).ready(function() {",
                "   var buttons = $('.button').prop('disabled', false);",
                "});",
                "</script>",
                "<table class='report-table' summary='%s'>" % self.quote(self.name),
            ]
        else:
            s = ["<table class='report-table' summary='%s'>" % self.quote(self.name)]
        # Render header
        s += ["<thead>"]
        s += ["<tr>"]
        if self.enumerate:
            s += ["<th>#</th>"]
        s += ["<th>%s</th>" % self.quote(c.title) for c in self.columns]
        s += ["</tr>"]
        s += ["</thead>"]
        s += ["<tbody>"]
        # Render data
        s_span = len(self.columns)
        if self.enumerate:
            s_span += 1
        current_section = None
        if self.data:
            n = 1
            for row in self.data:
                if isinstance(row, SectionRow):
                    # Display section row
                    if current_section and self.has_total and current_section.subtotal:
                        # Display totals from previous sections
                        s += render_subtotals()
                    s += [
                        ";".join(
                            [
                                "<tr><td colspan=%d style='margin: 0" % s_span,
                                "padding: 2px 5px 3px 5px;font-size: 11px;text-align:left",
                                "font-weight:bold",
                                "background: #7CA0C7 url(/ui/pkg/django-media/admin/img/default-bg.gif) top left repeat-x",
                                "color:white;'>",
                            ]
                        ),
                        self.quote(row.title),
                        "</td></tr>",
                    ]
                    current_section = row
                    continue
                s += ["<tr class='row%d'>" % (n % 2 + 1)]
                if self.enumerate:
                    s += ["<td align='right'>%d</td>" % n]
                n += 1
                for c, d in zip(self.columns, row):
                    s += [c.format_html(d)]
                    c.contribute_data(d)
                    if current_section:
                        current_section.contribute_data(c, d)
                s += ["</tr>"]
                # Render las subtotal
            if current_section and self.has_total and current_section.subtotal:
                # Display totals from previous sections
                s += render_subtotals()
            # Render totals
        if self.has_total:
            s += ["<tr>"]
            if self.enumerate:
                s += ["<td></td>"]
            for c in self.columns:
                s += [c.format_html_total()]
            s += ["</tr>"]
        s += ["</tbody>"]
        s += ["</table>"]
        return "\n".join(s)

    def to_csv(self, delimiter=","):
        """
        Return CSV representation of table
        :return:
        """
        f = StringIO()
        writer = csv.writer(f, delimiter=delimiter)
        if self.enumerate:
            writer.writerow(["#"] + [c.title for c in self.columns])
        else:
            writer.writerow([c.title for c in self.columns])
        if self.data:
            if self.enumerate:
                n = 1
                for row in self.data:
                    if isinstance(row, SectionRow):
                        writer.writerow([row.name])
                        continue
                    writer.writerow([n] + list(row))
                    n += 1
            else:
                for row in self.data:
                    if isinstance(row, SectionRow):
                        writer.writerow([row.name])
                        continue
                    writer.writerow(row)
        return f.getvalue()

    def to_ssv2(self, delimiter=";", mrf="center", date=None):
        """
        Return CSV representation of table
        :return:
        """
        f = StringIO()
        writer = csv.writer(f, delimiter=delimiter)
        section = "default"
        prefix = [mrf, section]
        prefix_c = ["mrf", "pool"]
        if date:
            prefix_c += ["date"]
            prefix += [date]
        if self.enumerate:
            writer.writerow(["#"] + prefix_c + [c.title for c in self.columns])
        else:
            writer.writerow(prefix_c + [c.title for c in self.columns])
        if self.data:
            if self.enumerate:
                n = 1
                for row in self.data:
                    if isinstance(row, SectionRow):
                        # writer.writerow([row.name])
                        prefix = [mrf, row.name]
                        if date:
                            prefix += [date]
                        continue
                    writer.writerow([n] + prefix + list(row))
                    n += 1
            else:
                for row in self.data:
                    if isinstance(row, SectionRow):
                        # writer.writerow([row.name])
                        prefix = [mrf, row.name]
                        if date:
                            prefix += [date]
                        continue
                    writer.writerow(prefix + list(row))
        return f.getvalue()


class MatrixSection(ReportSection):
    """
    Data is a list of (row, column, data)
    """

    def __init__(self, name, data=None, enumerate=False):
        super().__init__(name=name)
        self.data = data or []
        self.enumerate = enumerate

    def to_html(self, **kwargs):
        # Build rows and columns
        data = {}
        cl = set()
        rl = set()
        for r, c, d in self.data:
            rl.add(r)
            cl.add(c)
            data[r, c] = d
        cl = sorted(cl)
        rl = sorted(rl)
        # Render
        s = ["<table summary='%s' border='1'>" % self.quote(self.name)]
        # Header row
        s += ["<tr><th></th>"]
        if self.enumerate:
            s += ["<th></th>"]
        s += ["<th><div class='vtext'>%s</div></th>" % c for c in cl]
        # Data rows
        n = 0
        for r in rl:
            s += ["<tr class='row%d'>" % (n % 2 + 1)]
            if self.enumerate:
                s += ["<td align='right'>%d</td>" % (n + 1)]
            s += ["<td><b>%s</b></td>" % self.quote(r)]
            for c in cl:
                try:
                    s += ["<td>%s</td>" % self.quote(data[r, c])]
                except KeyError:
                    s += ["<td></td>"]
            n += 1
            s += ["</tr>"]
        return "\n".join(s)


class SimpleReport(ReportApplication):
    # List of PredefinedReport instances
    predefined_reports = {}

    def get_data(self, request, **kwargs):
        """
        Returns Report object
        """
        return Report()

    def report_html(self, include_buttons=True, **kwargs):
        """
        Render HTML
        """
        return self.get_data(**kwargs).to_html(include_buttons=include_buttons)

    def report_csv(self, **kwargs):
        """
        Render CSV
        """
        return self.get_data(**kwargs).to_csv()

    def from_dataset(self, title, columns, data, enumerate=False):
        """
        Shortcut to generate Report from dataset
        """
        r = Report()
        r.append_section(TextSection(title=title))
        r.append_section(TableSection(columns=columns, data=data, enumerate=enumerate))
        return r

    def from_query(self, title, columns, query, params=[], enumerate=False):
        """
        Shortcut to generate Report from SQL query
        """
        return self.from_dataset(
            title=title, columns=columns, data=self.execute(query, params), enumerate=enumerate
        )

    def get_predefined_args(self, variant):
        return self.predefined_reports[variant].args


class PredefinedReport(object):
    def __init__(self, title=None, args=None):
        self.title = title
        self.args = args or {}
