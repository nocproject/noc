from noc.main.report import BaseReport,Column
import os

class Report(BaseReport):
    title="Lines of code"
    requires_cursor=False
    columns=[Column("App"),Column(".py lines",align="RIGHT"),Column(".html lines",align="RIGHT")]
    
    def get_queryset(self):
        def loc(f):
            f=open(f)
            d=f.read()
            f.close()
            return len(d.split("\n"))
        r=[]
        for dirname in [d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith(".")]:
            py_loc=0
            html_loc=0
            for dirpath,dirnames,filenames in os.walk(dirname):
                for f in [f for f in filenames if f.endswith(".py")]:
                    py_loc+=loc(os.path.join(dirpath,f))
                for f in [f for f in filenames if f.endswith(".html")]:
                    html_loc+=loc(os.path.join(dirpath,f))
            r.append((dirname,py_loc,html_loc))
        return r
            