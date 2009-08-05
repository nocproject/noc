# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Time Patterns DSL compiler
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re,types

RC=re.compile
# Day of weeks declarations
DoW=["mon","tue","wen","thu","fri","sat","sun"]

DoWRE="(%s)"%("|".join(DoW))
# Day part patterns
DAY_PATTERNS=[
    (RC(r"^(\d{2})$"),                           lambda day:             "(T.day==%d)"%int(day)),
    (RC(r"^(\d{2})-(\d{2})$"),                   lambda from_day,to_day: "(%d<=T.day<=%d)"%(int(from_day),int(to_day))),
    (RC(r"^(\d{2})\.(\d{2})$"),                  lambda day,month:       "(T.day==%d and T.month==%d)"%(int(day),int(month))),
    (RC(r"^(\d{2})\.(\d{2})-(\d{2})\.(\d{2})$"), lambda from_day,from_month,to_day,to_month: "('%s%s'<=('%%02d%%02d'%%(T.month,T.day))<='%s%s')"%(from_month,from_day,to_month,to_day)),
    (RC(r"^(\d{2})\.(\d{2})\.(\d{4})$"),         lambda day,month,year:  "(T.day==%d and T.month==%d and T.year==%d)"%(int(day),int(month),int(year))),
    (RC(r"^(\d{2})\.(\d{2})\.(\d{4})-(\d{2})\.(\d{2})\.(\d{4})$"),
                                                 lambda from_day,from_month,from_year,to_day,to_month,to_year: "('%s%s%s'<=('%%04d%%02d%%02d'%%(T.year,T.month,T.day))<='%s%s%s')"%(from_year,from_month,from_day,to_year,to_month,to_day)),
    (RC(r"^%s$"%DoWRE,re.IGNORECASE),            lambda dow:             "(T.weekday()==%d)"%DoW.index(dow.lower())),
    (RC(r"^%s-%s$"%(DoWRE,DoWRE),re.IGNORECASE), lambda from_dow,to_dow: "(%d<=T.weekday()<=%d)"%(DoW.index(from_dow.lower()),DoW.index(to_dow))),
]

# Time part patterns
TIME_PATTERNS=[
    (RC(r"^(\d{2}):(\d{2})$"),                 lambda hour,minute:                             "(T.hour==%d and T.minute==%d)"%(int(hour),int(minute))),
    (RC(r"^(\d{2}):(\d{2})-(\d{2}):(\d{2})$"), lambda from_hour,from_minute,to_hour,to_minute: "(%d<=(T.hour*60+T.minute)<=%d)"%(int(from_hour)*60+int(from_minute),int(to_hour)*60+int(to_minute))),
]
##
##
##
class TimePattern(object):
    """
    >>> import datetime
    >>> TimePattern("13").match(datetime.datetime(year=2005,month=3,day=13))
    True
    >>> TimePattern("02").match(datetime.datetime(year=2005,month=3,day=13))
    False
    >>> TimePattern("01-15").match(datetime.datetime(year=2005,month=3,day=13))
    True
    >>> TimePattern("01.03").match(datetime.datetime(year=2005,month=3,day=13))
    False
    >>> TimePattern("13.03").match(datetime.datetime(year=2005,month=3,day=13))
    True
    >>> TimePattern("01.03-02.04").match(datetime.datetime(year=2005,month=3,day=13))
    True
    >>> TimePattern("13.03.2005").match(datetime.datetime(year=2005,month=3,day=13))
    True
    >>> TimePattern("01.03.2005-15.03.2005").match(datetime.datetime(year=2005,month=3,day=13))
    True
    >>> TimePattern("sun").match(datetime.datetime(year=2005,month=3,day=13))
    True
    >>> TimePattern("fri").match(datetime.datetime(year=2005,month=3,day=13))
    False
    >>> TimePattern("fri-sun").match(datetime.datetime(year=2005,month=3,day=13))
    True
    """
    def __init__(self,pattern):
        self.code=compile(self.compile_to_python(pattern),"<string>","eval")
    ## Check datetime object matches time pattern
    ## Returns True or False
    def match(self,d):
        return eval(self.code,{"T":d})
    ##
    ## Convert a string of a list of time pattern declarations to the python expression
    ##
    def compile_to_python(self,tp):
        def compile_pattern(P,p):
            for l,r in P:
                match=l.match(p)
                if match:
                    return r(*match.groups())
            raise SyntaxError,"Invalid expression '%s'"%p
        if tp is None:
            return "True"
        if type(tp) in (types.ListType,types.TupleType):
            if len(tp)==0:
                return "True"
            return "(%s)"%(" or ".join([self.compile_to_python(p) for p in tp]))
        tp=tp.strip()
        if "|" in tp:
            day_pattern,time_pattern=tp.split("|")
        else:
            day_pattern=tp
            time_pattern=""
        dpl=" or ".join([compile_pattern(DAY_PATTERNS,x.strip()) for x in day_pattern.split(",") if x])
        tpl=" or ".join([compile_pattern(TIME_PATTERNS,x.strip()) for x in time_pattern.split(",") if x])
        x=" and ".join(["(%s)"%x for x in [dpl,tpl] if x])
        if not x:
            return "True"
        else:
            return x
##
## Enclosure for a list of time patterns
##
class TimePatternList(object):
    def __init__(self,patterns):
        self.patterns=patterns
    def match(self,d):
        for tp in self.patterns:
            if not tp.match(d):
                return False
        return True
#
# Tests
#
if __name__ == "__main__":
    import doctest
    doctest.testmod()
