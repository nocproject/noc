## Django modules
from django.db import models


class Style(models.Model):
    """
    CSS Style
    """
    class Meta:
        verbose_name = "Style"
        verbose_name_plural = "Styles"
        ordering = ["name"]
        app_label = "main"
        db_table = "main_style"

    name = models.CharField("Name", max_length=64, unique=True)
    font_color = models.IntegerField("Font Color", default=0)
    background_color = models.IntegerField("Background Color", default=0xffffff)
    bold = models.BooleanField("Bold", default=False)
    italic = models.BooleanField("Italic", default=False)
    underlined = models.BooleanField("Underlined", default=False)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def css_class_name(self):
        """
        CSS Class Name
        """
        return u"noc-color-%d" % self.id

    @property
    def style(self):
        """
        CSS Style
        """
        s = u"color: #%06X !important; background-color: #%06X !important;" % (
            self.font_color, self.background_color)
        if self.bold:
            s += u" font-weight: bold !important;"
        if self.italic:
            s += u" font-style: italic !important;"
        if self.underlined:
            s += u" text-decoration: underline !important;"
        return s

    @property
    def css(self):
        """
        CSS class style
        """
        return u".%s, .%s td { %s }\n" % (
            self.css_class_name, self.css_class_name, self.style)
