# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SimpleReport implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import cStringIO
import csv
import decimal
import types
import pprint
## Django modules
from django.utils.dateformat import DateFormat
## NOC modules
from reportapplication import *
from noc import settings
from noc.lib.widgets import tags_list

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
        return unicode(s).replace("&", "&amp;").replace(
            "<", "&lt;").replace(">", "&gt;").replace(
            "\"", "&quot;").replace("'", "&#39;")

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

    def to_html(self):
        """
        Return HTML presentation of Node
        """
        return ""

    def to_csv(self):
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
        super(Report, self).__init__(name=name)
        self.sections = []  # Must be ReportSection instances

    def append_section(self, s):
        self.sections += [s]

    ##
    ## Return XML code for report
    ##
    def to_xml(self):
        s = [self.format_opening_xml_tag(name=self.name)]
        s += [self.indent("<sections>")]
        s += [self.indent(x.to_xml(), 2) for x in self.sections]
        s += [self.indent("</sections>")]
        s += [self.format_closing_xml_tag()]
        return "\n".join(s)

    ##
    ## Return HTML code for report
    ##
    def to_html(self):
        return "\n".join([s.to_html() for s in self.sections])

    ##
    ## Return CSV for report
    ##
    def to_csv(self):
        return "\n".join([x for x in [s.to_csv() for s in self.sections] if x])


class ReportSection(ReportNode):
    """
    Abstract class for report sections
    """
    pass


class TextSection(ReportSection):
    """
    Section containing text. Consists of title and text
    text bay be string or list of paragraphs.
    Skipped in CSV mode
    """
    tag = "text"

    def __init__(self, name=None, title=None, text=None):
        super(ReportSection, self).__init__(name=name)
        self.title = title
        self.text = text  # Either string o list of strings

    @property
    def paragraphs(self):
        """
        Returns a list of paragraphs
        """
        if not self.text:
            return []
        if isinstance(self.text, basestring):
            return [self.text]
        else:
            return self.text

    def to_xml(self):
        """
        Return XML presentation of text section
        """
        s = [self.format_opening_xml_tag(name=self.name, title=self.title)]
        s += [self.indent("<par>%s</par>" % self.quote(p)) for p in
              self.paragraphs]
        s += [self.format_closing_xml_tag()]
        return "\n".join(s)

    def to_html(self):
        """
        Return HTML presentation of text section
        """
        s = []
        if self.title:
            s += ["<h2>%s</h2>" % self.quote(self.title)]
        s += ["<p>%s</p>" % self.quote(p) for p in self.paragraphs]
        return "\n".join(s)


##
## Precomputed size multipliers
## List of (limit, divider, suffix)
##
SIZE_DATA = []
l = decimal.Decimal(1024)
for suffix in ["KB", "MB", "GB", "TB", "PB"]:
    SIZE_DATA += [(l * 1024, l, suffix)]
    l *= 1024


class SafeString(unicode):
    """
    Do not perform HTML quoting
    """
    pass


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

    def __init__(self, name, title=None, align=None, format=None, total=None,
                 total_label=None):
        self.name = name
        self.title = title if title else name
        self.align = {"l": self.ALIGN_LEFT, "left": self.ALIGN_LEFT,
                      "r": self.ALIGN_RIGHT, "right": self.ALIGN_RIGHT,
                      "c": self.ALIGN_CENTER, "center": self.ALIGN_CENTER}[
        align.lower()] if align else None
        self.format = getattr(self, "f_%s" % format) if isinstance(format,
                                                        basestring) else format
        self.total = getattr(self, "ft_%s" % total) if isinstance(total,
                                                        basestring) else total
        self.total_label = total_label
        self.total_data = []
        self.subtotal_data = []

    ##
    ## Check column has total
    ##
    @property
    def has_total(self):
        return self.total

    ##
    ## Reset sub-totals
    ##
    def start_section(self):
        self.subtotal_data = []

    ##
    ## Contribute data to totals
    ##
    def contribute_data(self, s):
        if self.total:
            self.total_data += [s]

    ##
    ## Return formatted cell
    ##
    def format_data(self, s):
        if s is None or s == "":
            return ""
        elif not self.format:
            return s
        else:
            return self.format(s)

    ##
    ## Return XML representation of column
    ##
    def to_xml(self):
        return self.format_opening_xml_tag(name=self.name,
                                           align=self.align) + self.quote(
            self.title) + self.format_closing_xml_tag()

    ##
    ## Return quoted HTML TD attributes
    ##
    def html_td_attrs(self):
        attrs = {}
        if self.align:
            if self.align & self.H_ALIGN_MASK == self.ALIGN_LEFT:
                attrs["align"] = "left"
            elif self.align & self.H_ALIGN_MASK == self.ALIGN_RIGHT:
                attrs["align"] = "right"
            elif self.align & self.H_ALIGN_MASK == self.ALIGN_CENTER:
                attrs["align"] = "center"
        return " " + " ".join(
            ["%s='%s'" % (k, self.quote(v)) for k, v in attrs.items()])

    ##
    ## Render single cell
    ##
    def format_html(self, s):
        d = self.format_data(s)
        if type(d) != SafeString:
            d = self.quote(d)
        return "<td%s>%s</td>" % (self.html_td_attrs(), d)

    ##
    ## Render totals
    ##
    def format_html_total(self):
        if self.total:
            total = self.format_data(self.total(self.total_data))
        elif self.total_label:
            total = self.total_label
        else:
            total = ""
        return "<td%s><b>%s</b></td>" % (self.html_td_attrs(), total)

    ##
    ## Render subtotals
    ##
    def format_html_subtotal(self, d):
        if self.total:
            total = self.format_data(self.total(d))
        elif self.total_label:
            total = self.total_label
        else:
            total = ""
        return "<td%s><b>%s</b></td>" % (self.html_td_attrs(), total)

    ##
    ## Display date according to settings
    ##
    def f_date(self, f):
        return DateFormat(f).format(settings.DATE_FORMAT)

    ##
    ## Display time according to settings
    ##
    def f_time(self, f):
        return DateFormat(f).format(settings.TIME_FORMAT)

    ##
    ## Display date and time according to settings
    ##
    def f_datetime(self, f):
        return DateFormat(f).format(settings.DATETIME_FORMAT)

    ##
    ## Display pretty size
    ##
    def f_size(self, f):
        f = decimal.Decimal(f)
        for limit, divider, suffix in SIZE_DATA:
            if f < limit:
                return ("%8.2f%s" % (f / divider, suffix)).strip()
        limit, divider, suffix = SIZE_DATA[-1]
        return ("%8.2%s" % (f / divider, suffix)).strip()

    ##
    ## Display pretty numeric
    ##
    def f_numeric(self, f):
        if not f:
            return "0"
        if type(f) == types.FloatType:
            f = str(f)
        try:
            f = decimal.Decimal(f)
        except decimal.InvalidOperation:
            return "-"
        sign, digits, exp = f.as_tuple()
        if exp:
            r = "." + "".join(map(str, digits[-exp:]))
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
            return SafeString("<img src='/static/pkg/famfamfam-silk/tick.png' />")
        else:
            return SafeString("<img src='/static/pkg/famfamfam-silk/cross.png' />")

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

    def f_pprint(self, l):
        """
        Returns a pretty-printed object
        """
        return SafeString("<pre>%s</pre>" % pprint.pformat(l))

    def f_tags(self, f):
        """
        Display and object's tags
        """
        try:
            return SafeString(tags_list(f))
        except:
            return ""

    def ft_sum(self, l):
        """
        Returns a sum of not-null elements
        """
        return reduce(lambda x, y: x + y,
            [decimal.Decimal(str(z)) for z in l if z], 0)

    def ft_count(self, l):
        """
        Returns a count of not-null elements
        """
        return len([x for x in l if x])


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


##
## Section containing table
##
##
class TableSection(ReportSection):
    tag = "table"

    def __init__(self, name=None, columns=[], enumerate=False, data=[]):
        super(ReportSection, self).__init__(name=name)
        self.columns = []
        for c in columns:
            if isinstance(c, basestring) or hasattr(c, "__unicode__"):
                self.columns += [TableColumn(unicode(c))]
            else:
                self.columns += [c]
        self.data = data
        self.enumerate = enumerate
        self.has_total = reduce(lambda x, y: x or y,
            [c.has_total for c in self.columns],
                                False)  # Check wrether table has totals

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

    ##
    ## Return HTML representation of table
    ##
    def to_html(self):
        def render_subtotals():
            if not current_section.data:
                return []
            s = ["<tr style='font-style:italic;background-color:#C0C0C0'>"]
            if self.enumerate:
                s += ["<td></td>"]
            s += [c.format_html_subtotal(current_section.data[c]) for c in
                  self.columns]
            s += ["</tr>"]
            return s

        t_id = "reporttable-%d" % id(self)
        s = [
            "<script type='text/javascript' src='/static/js/jquery.table2CSV.js'></script>",
            "<table  id='%s' class='report-table' summary='%s'>" % (t_id, self.quote(self.name))
        ]
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
                if type(row) == SectionRow:
                    # Display section row
                    if (current_section and self.has_total and
                        current_section.subtotal):
                        # Display totals from previous sections
                        s += render_subtotals()
                    s += [
                        "<tr><td colspan=%d style='margin: 0;padding: 2px 5px 3px 5px;font-size: 11px;text-align:left;font-weight:bold;background: #7CA0C7 url(/media/admin/img/default-bg.gif) top left repeat-x;color:white;'>" % s_span,
                        self.quote(row.title), "</td></tr>"]
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
            if (current_section and self.has_total and
                current_section.subtotal):
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
        s += ["<form action='/main/desktop/dlproxy/' method='POST'>"]
        s += ["<input type='hidden' name='content_type' value='text/csv; charset=utf8'>"]
        s += ["<input type='hidden' name='filename' value='report.csv'>"]
        s += ["<input type='hidden' name='data' id='csv_data'>"]
        s += ["<input type='submit' value='CSV' onclick='getCSVData(\"%s\");'>" % t_id]
        s += ["</form>"]
        s += ["<script>"]
        s += ["function getCSVData(t) {"]
        s += ["var v = $('#' + t).table2CSV({delivery: 'value', separator: ';'});"]
        s += ["$('#csv_data').val(v);"]
        s += ["}"]
        s += ["</script>"]
        return "\n".join(s)

    ##
    ## Return CSV representation of table
    ##
    def to_csv(self):
        f = cStringIO.StringIO()
        writer = csv.writer(f)
        if self.enumerate:
            writer.writerow(["#"] + [c.title for c in self.columns])
        else:
            writer.writerow([c.title for c in self.columns])
        if self.data:
            if self.enumerate:
                n = 1
                for row in self.data:
                    if type(row) == SectionRow:
                        continue
                    writer.writerow([n] + list(row))
                    n += 1
            else:
                for row in self.data:
                    if type(row) == SectionRow:
                        continue
                    writer.writerow(row)
        return f.getvalue()


##
##
##
class MatrixSection(ReportSection):
    ##
    ## Data is a list of (row,column,data)
    ##
    def __init__(self, name, data=[], enumerate=False):
        super(ReportSection, self).__init__(name=name)
        self.data = data
        self.enumerate = enumerate

    def to_html(self):
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
    def get_data(self, **kwargs):
        """
        Returns Report object
        """
        return Report()

    def report_html(self, **kwargs):
        """
        Render HTML
        """
        return self.get_data(**kwargs).to_html()

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
        r.append_section(
            TableSection(columns=columns, data=data, enumerate=enumerate))
        return r

    def from_query(self, title, columns, query, params=[], enumerate=False):
        """
        Shortcut to generate Report from SQL query
        """
        return self.from_dataset(title=title, columns=columns,
                                 data=self.execute(query, params),
                                 enumerate=enumerate)
