# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various debugging utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import sys,re,logging,datetime,os,tempfile,cPickle,time,gc,random,stat

#
# Error reporting context
#
DEBUG_CTX_COMPONENT=None
DEBUG_CTX_CRASH_DIR=None
DEBUG_CTX_CRASH_PREFIX="crashinfo-"
DEBUG_CTX_SET_UID=None
#
def set_crashinfo_context(component,crash_dir):
    global DEBUG_CTX_COMPONENT,DEBUG_CTX_CRASH_DIR,DEBUG_CTX_SET_UID
    DEBUG_CTX_COMPONENT=component
    DEBUG_CTX_CRASH_DIR=crash_dir
    if os.getuid()==0: # Daemon launched as a root
        DEBUG_CTX_SET_UID=os.stat(crash_dir)[stat.ST_UID]

# Borrowed from django
def get_lines_from_file(filename,lineno,context_lines,loader=None,module_name=None):
    """
    Returns context_lines before and after lineno from file.
    Returns (pre_context_lineno, pre_context, context_line, post_context).
    """
    source = None
    if loader is not None and hasattr(loader, "get_source"):
        source = loader.get_source(module_name)
        if source is not None:
            source = source.splitlines()
    if source is None:
        try:
            f = open(filename)
            try:
                source = f.readlines()
            finally:
                f.close()
        except (OSError, IOError):
            pass
    if source is None:
        return None, [], None, []
    encoding = 'ascii'
    for line in source[:2]:
        # File coding may be specified. Match pattern from PEP-263
        # (http://www.python.org/dev/peps/pep-0263/)
        match = re.search(r'coding[:=]\s*([-\w.]+)', line)
        if match:
            encoding = match.group(1)
            break
    source = [unicode(sline, encoding, 'replace') for sline in source]
    lower_bound = max(0, lineno - context_lines)
    upper_bound = lineno + context_lines
    pre_context = [line.strip('\n') for line in source[lower_bound:lineno]]
    context_line = source[lineno].strip('\n')
    post_context = [line.strip('\n') for line in source[lineno+1:upper_bound]]
    return lower_bound, pre_context, context_line, post_context

# Borrowed from django
def get_traceback_frames(tb):
    frames = []
    while tb is not None:
        # support for __traceback_hide__ which is used by a few libraries
        # to hide internal frames.
        if tb.tb_frame.f_locals.get('__traceback_hide__'):
            tb = tb.tb_next
            continue
        filename = tb.tb_frame.f_code.co_filename
        function = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno - 1
        loader = tb.tb_frame.f_globals.get('__loader__')
        module_name = tb.tb_frame.f_globals.get('__name__')
        pre_context_lineno, pre_context, context_line, post_context = get_lines_from_file(filename, lineno, 7, loader, module_name)
        if pre_context_lineno is not None:
            frames.append({
                'tb': tb,
                'filename': filename,
                'function': function,
                'lineno': lineno + 1,
                'vars': tb.tb_frame.f_locals.items(),
                'id': id(tb),
                'pre_context': pre_context,
                'context_line': context_line,
                'post_context': post_context,
                'pre_context_lineno': pre_context_lineno + 1,
            })
        tb = tb.tb_next
    if not frames:
        frames = [{
            'filename': 'unknown',
                    'function': '?',
                    'lineno': '?',
                    'context_line': '???',
                }]
    return frames

def get_execution_frames(frame):
    e_f=[]
    while frame is not None:
        e_f.append(frame)
        frame=frame.f_back
    e_f.reverse()
    frames = []
    for frame in e_f:
        filename = frame.f_code.co_filename
        function = frame.f_code.co_name
        lineno = frame.f_lineno - 1
        loader = frame.f_globals.get('__loader__')
        module_name = frame.f_globals.get('__name__')
        pre_context_lineno, pre_context, context_line, post_context = get_lines_from_file(filename, lineno, 7, loader, module_name)
        if pre_context_lineno is not None:
            frames.append({
                'filename': filename,
                'function': function,
                'lineno': lineno + 1,
                'vars': frame.f_locals.items(),
                'pre_context': pre_context,
                'context_line': context_line,
                'post_context': post_context,
                'pre_context_lineno': pre_context_lineno + 1,
            })
    if not frames:
        frames = [{
            'filename': 'unknown',
                    'function': '?',
                    'lineno': '?',
                    'context_line': '???',
                }]
    return frames

def format_frames(frames):
    def format_source(lineno,lines):
        r=[]
        for l in lines:
            r+=["%5d     %s"%(lineno,l)]
            lineno+=1
        return "\n".join(r)
    r=[]
    r+=["START OF TRACEBACK"]
    r+=["-"*72]
    for f in frames:
        r+=["File: %s (Line: %d)"%(f["filename"],f["lineno"])]
        r+=["Function: %s"%(f["function"])]
        r+=[format_source(f["pre_context_lineno"],f["pre_context"])]
        r+=["%5d ==> %s"%(f["lineno"],f["context_line"])]
        r+=[format_source(f["lineno"]+1,f["post_context"])]
        r+=["Variables:"]
        for n,v in f["vars"]:
            r+=["%20s = %s"%(n,repr(v))]
        r+=["-"*72]
    r+=["END OF TRACEBACK"]
    return "\n".join(r)

def error_report():
    t,v,tb=sys.exc_info()
    now=datetime.datetime.now()
    r=["UNHANDLED EXCEPTION (%s)"%str(now)]
    r+=["Working directory: %s"%os.getcwd()]
    r+=[str(t),str(v)]
    r+=[format_frames(get_traceback_frames(tb))]
    r="\n".join(r)
    logging.error(r)
    if DEBUG_CTX_COMPONENT and DEBUG_CTX_CRASH_DIR:
        c={
            "source"    : "system",
            "type"      : "Unhandled Exception",
            "ts"        : int(time.time()),
            "component" : DEBUG_CTX_COMPONENT,
            "traceback" : r,
        }
        h,p=tempfile.mkstemp(suffix="",prefix=DEBUG_CTX_CRASH_PREFIX,dir=DEBUG_CTX_CRASH_DIR)
        f=os.fdopen(h,"w")
        f.write(cPickle.dumps(c))
        f.close()
        if DEBUG_CTX_SET_UID: # Change crashinfo userid to directory's owner
            os.chown(p,DEBUG_CTX_SET_UID,-1)

def frame_report(frame):
    now=datetime.datetime.now()
    r=["EXECUTION FRAME REPORT (%s)"%str(now)]
    r+=["Working directory: %s"%os.getcwd()]
    r+=[format_frames(get_execution_frames(frame))]
    logging.error("\n".join(r))
##
## Garbage collection profiling
## Instance created on daemon start
##
class GCStats(object):
    def __init__(self):
        self.history={}
    ##
    def get_history(self,t):
        if t in self.history:
            return str(self.history[t])
        else:
            return "[]"
    ##
    ## Collect GC info and prepare report
    ##
    def report(self):
        # Collect all collectable trash
        gc.collect()
        # Calculate type counts
        counts={}
        ref_counts={}
        for obj in gc.get_objects():
            objtype=type(obj)
            if objtype in counts:
                counts[objtype]+=1
            else:
                counts[objtype]=1
            if objtype not in ref_counts:
                ref_counts[objtype]={}
            # Update referrers counters
            for ro in gc.get_referents(obj):
                robjtype=type(ro)
                if robjtype not in ref_counts:
                    ref_counts[robjtype]={}
                rc=ref_counts[robjtype]
                if objtype in rc:
                    rc[objtype]+=1
                else:
                    rc[objtype]=1
        # Update history
        for t,c in counts.iteritems():
            if t in self.history:
                self.history[t]=([c]+self.history[t])[:10]
            else:
                self.history[t]=[c]
        sc=sorted(counts.iteritems(),lambda x,y:-cmp(x[1],y[1]))
        # Generaate report
        r=["OBJECT REFERENCE COUNT:"]
        r+=["Total objects: %d"%len(gc.get_objects())]
        r+=["%80s: %10d %s"%("%s.%s"%(c[0].__module__,c[0].__name__),c[1],self.get_history(c[0])) for c in sc]
        # Referrers to top 5 objects
        for t,c in sc[:5]:
            r+=["REFERRERS TO: %s.%s"%(t.__module__,t.__name__)]
            rc=sorted(ref_counts[t].iteritems(),lambda x,y:-cmp(x[1],y[1]))
            r+=["    %80s: %10d"%("%s.%s"%(c[0].__module__,c[0].__name__),c[1]) for c in rc]
        # Random object report
        N=100 # N of samples
        S=sc[0][1] # Top used objects count
        T=sc[0][0] # Top used type
        L=max(S/N,1)
        r+=["RANDOM %d TOP USED OBJECTS:"%S]
        for o in gc.get_objects():
            if type(o)==T:
                if random.randint(0,S)<=L:
                    r+=[str(o)]
                    N-=1
                    if N==0:
                        break
        r+=["END OF OBJECT REFERENCE COUNT"]
        return "\n".join(r)
    ##
    ##
    ##
    def report_dot(self):
        gc.collect()
        
