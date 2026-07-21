# ---------------------------------------------------------------------
# Time Patterns DSL compiler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

RC = re.compile
# Day of weeks declarations
DoW = ["mon", "tue", "wen", "thu", "fri", "sat", "sun"]

DoWRE = "({})".format("|".join(DoW))
# Day part patterns
DAY_PATTERNS = [
    (RC(r"^(\d{2})$"), lambda day: "(T.day == %d)" % int(day)),
    (
        RC(r"^(\d{2})-(\d{2})$"),
        lambda from_day, to_day: "(%d <= T.day <= %d)" % (int(from_day), int(to_day)),
    ),
    (
        RC(r"^(\d{2})\.(\d{2})$"),
        lambda day, month: "(T.day == %d and T.month == %d)" % (int(day), int(month)),
    ),
    (
        RC(r"^(\d{2})\.(\d{2})-(\d{2})\.(\d{2})$"),
        lambda from_day, from_month, to_day, to_month: (
            f"('{from_month}{from_day}' <= ('%02d%02d' % (T.month, T.day)) <= '{to_month}{to_day}')"
        ),
    ),
    (
        RC(r"^(\d{2})\.(\d{2})\.(\d{4})$"),
        lambda day, month, year: (
            "(T.day == %d and T.month == %d and T.year == %d)" % (int(day), int(month), int(year))
        ),
    ),
    (
        RC(r"^(\d{2})\.(\d{2})\.(\d{4})-(\d{2})\.(\d{2})\.(\d{4})$"),
        lambda from_day, from_month, from_year, to_day, to_month, to_year: (
            f"('{from_year}{from_month}{from_day}' <= ('%04d%02d%02d' % (T.year, T.month, T.day)) <= '{to_year}{to_month}{to_day}')"
        ),
    ),
    (
        RC(rf"^{DoWRE}$", re.IGNORECASE),
        lambda dow: "(T.weekday() == %d)" % DoW.index(dow.lower()),
    ),
    (
        RC(rf"^{DoWRE}-{DoWRE}$", re.IGNORECASE),
        lambda from_dow, to_dow: (
            "(%d <= T.weekday() <= %d)" % (DoW.index(from_dow.lower()), DoW.index(to_dow))
        ),
    ),
]

# Time part patterns
TIME_PATTERNS = [
    (
        RC(r"^(\d{2}):(\d{2})$"),
        lambda hour, minute: "(T.hour == %d and T.minute == %d)" % (int(hour), int(minute)),
    ),
    (
        RC(r"^(\d{2}):(\d{2})-(\d{2}):(\d{2})$"),
        lambda from_hour, from_minute, to_hour, to_minute: (
            "(%d <= (T.hour * 60 + T.minute) <= %d)"
            % (int(from_hour) * 60 + int(from_minute), int(to_hour) * 60 + int(to_minute))
        ),
    ),
]


class TimePattern:
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
    >>> TimePattern("zho")
    Traceback (most recent call last):
    ...
    SyntaxError: Invalid expression 'zho'
    >>> TimePattern(None).match(datetime.datetime(year=2005,month=3,day=13))
    True
    """

    def __init__(self, pattern) -> None:
        self.code = compile(self.compile_to_python(pattern), "<string>", "eval")

    def match(self, d):
        """
        Check datetime object matches time pattern
        :return: Boolean result
        """
        return eval(self.code, {"T": d})

    @classmethod
    def compile_to_python(cls, tp):
        """
        Convert a string of a list of time pattern declarations
        to the python expression
        :return:
        """

        def compile_pattern(P, p):
            for l, r in P:
                match = l.match(p)
                if match:
                    return r(*match.groups())
            raise SyntaxError(f"Invalid expression '{p}'")

        if tp is None:
            return "True"
        if isinstance(tp, (list, tuple)):
            if not tp:
                return "True"
            return "({})".format(" or ".join([cls.compile_to_python(p) for p in tp]))
        tp = tp.strip()
        if "|" in tp:
            day_pattern, time_pattern = tp.split("|")
        else:
            day_pattern = tp
            time_pattern = ""
        dpl = " or ".join(
            [compile_pattern(DAY_PATTERNS, x.strip()) for x in day_pattern.split(",") if x]
        )
        tpl = " or ".join(
            [compile_pattern(TIME_PATTERNS, x.strip()) for x in time_pattern.split(",") if x]
        )
        x = " and ".join([f"({x})" for x in [dpl, tpl] if x])
        if not x:
            return "True"
        return x


class TimePatternList:
    """
    Enclosure for a list of time patterns
    """

    def __init__(self, patterns) -> None:
        self.patterns = patterns

    def match(self, d):
        return all(tp.match(d) for tp in self.patterns)
