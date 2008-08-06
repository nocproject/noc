##
##
##
import os,tempfile

def safe_rewrite(path,text):
    d=os.path.dirname(path)
    b=os.path.basename(path)
    h,p=tempfile.mkstemp(suffix=".tmp",prefix=b,dir=d)
    f=os.fdopen(h,"w")
    f.write(text)
    f.close()
    if os.path.exists(path):
        os.unlink(path)
    os.link(p,path)
    os.unlink(p)