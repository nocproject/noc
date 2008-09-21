##
##
##
import os,tempfile,sha

def safe_rewrite(path,text):
    d=os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)
    b=os.path.basename(path)
    h,p=tempfile.mkstemp(suffix=".tmp",prefix=b,dir=d)
    f=os.fdopen(h,"w")
    f.write(text)
    f.close()
    if os.path.exists(path):
        os.unlink(path)
    os.link(p,path)
    os.unlink(p)
##
## Check file content is differ from string
##
def is_differ(path,content):
    if os.path.isfile(path):
        f=open(path)
        cs1=sha.sha(f.read()).digest()
        f.close()
        cs2=sha.sha(content).digest()
        return cs1!=cs2
    else:
        return True
##
## Rewrites file when content is differ
## Returns boolean signalling wherher file was rewritten
##
def rewrite_when_differ(path,content):
    d=is_differ(path,content)
    if d:
        safe_rewrite(path,content)
    return d
##
## Read file and return file's content.
## Return None when file does not exists
##
def read_file(path):
    if os.path.exists(path):
        f=open(path,"r")
        data=f.read()
        f.close()
        return data
    else:
        return None
            
    