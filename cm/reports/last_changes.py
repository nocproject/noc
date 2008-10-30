from noc.main.report import Column
import noc.main.report
from noc.cm.models import Object
from django import forms
import datetime

class ReportForm(forms.Form):
    repo=forms.ChoiceField(label="Type",choices=[("config","config"),("dns","dns"),("prefix-list","prefix-list")])
    days=forms.IntegerField(label="In Days",min_value=1)

class Report(noc.main.report.Report):
    name="cm.last_changes"
    title="Latest Changes"
    form_class=ReportForm
    columns=[
            Column("Object",format=lambda o:"<A HREF='/cm/view/%s/%s/'>%s</A>"%(o.repo_name,o.id,o.repo_path)),
            Column("Last Changed")
            ]
    
    def get_queryset(self):
        oc=Object.get_object_class(self.form.cleaned_data["repo"])
        baseline=datetime.datetime.now()-datetime.timedelta(days=self.form.cleaned_data["days"])
        r=[]
        for o in oc.objects.all():
            lm=o.last_modified
            if lm and lm>baseline:
                r+=[[o,lm]]
        r.sort(lambda x,y:-cmp(x[1],y[1]))
        return r
