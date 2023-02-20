# ----------------------------------------------------------------------
# CSV DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Any, Optional, Tuple

# Third-party modules
from jinja2 import Template as Jinja2Template

# NOC modules
from .base import DataFormatter
from ..types import OutputType, BandFormat
from noc.services.web.base.simplereport import (
    Report,
    TextSection,
    TableSection,
    SectionRow,
    TableColumn,
)


class TableFormatter(DataFormatter):
    def render_document(self):
        """

        :return:
        """
        report = Report()
        rband_format = self.get_band_format(self.root_band.name)
        report.append_section(
            TextSection(title=rband_format.title_template if rband_format else "")
        )
        columns, fields = self.get_columns()
        report.append_section(
            TableSection(
                columns=list(columns),
                data=self.get_report_data(fields),
                enumerate=False,
            )
        )
        if self.report_template.output_type == OutputType.CSV:
            r = report.to_csv(delimiter=",")
        elif self.report_template.output_type == OutputType.SSV:
            r = report.to_csv(delimiter=";")
        elif self.report_template.output_type == OutputType.HTML:
            r = report.to_html()
        self.output_stream.write(r.encode("utf8"))

    def get_report_data(self, columns: List[str] = None) -> List[Any]:
        """
        Convert Report Band to Report Data Section
        :return:
        """
        r = []
        for rb in self.root_band.iter_all_bands():
            # Section Row
            if rb.parent:  # Section
                bf = self.get_band_format(rb.name)
                if bf and bf.title_template:
                    r.append(SectionRow(self.get_title(rb, bf.title_template)))
            # Out data
            if not rb.has_children and rb.rows is not None and not rb.rows.is_empty():
                row_columns = columns or rb.rows.columns
                for row in rb.rows.to_dicts():
                    r.append([row.get(c, "") for c in row_columns])
        return r

    def get_band_format(self, name: str) -> Optional[BandFormat]:
        """

        :return:
        """
        if not self.report_template.bands_format or name not in self.report_template.bands_format:
            return
        return self.report_template.bands_format[name]

    def get_columns(self) -> Tuple[List[Any], Optional[List[str]]]:
        """
        Return columns format and fields list
        :return:
        """
        # Try Root config first
        band_format = self.get_band_format(self.root_band.name)
        fields = None
        # Try DataBand
        if not band_format or not band_format.columns:
            band = self.root_band.get_data_band()
            band_format = self.get_band_format(band.name)
            fields = [c.name for c in band_format.columns] if band_format else None
        if not band_format:
            return ([fn for fn in band.rows.columns],) * 2
        columns = []
        for c in band_format.columns:
            if c.format_type or c.total:
                columns += [
                    TableColumn(
                        c.title or "",
                        align=c.align.name.lower(),
                        format=c.format_type,
                        total=c.total,
                        total_label=c.total_label,
                    )
                ]
            else:
                columns += [c.title or ""]
        return columns, fields

    @staticmethod
    def get_title(band, template: Optional[str] = None) -> str:
        """
        Render Band Title if setting template
        :return:
        """
        if not template:
            return band.name
        return Jinja2Template(template).render(band.get_data())
