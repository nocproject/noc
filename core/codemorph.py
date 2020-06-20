# ----------------------------------------------------------------------
# code_morph function
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from typing import Dict, Any, Callable
import inspect
from types import FunctionType, MethodType
from threading import Lock

# NOC modules
from noc.core.hash import hash_int


class CodeMorpher(object):
    rx_open = re.compile(r"\n?\s*# (if) (.+?)\s+{\s*\n", re.MULTILINE)
    rx_close = re.compile(r"\n\s*# }\s*\n", re.MULTILINE)
    rx_if = re.compile(r"^(\s*)if ([^:]+):\n", re.MULTILINE)
    lock = Lock()
    cache = {}

    @classmethod
    def code_morph_text(cls, src: str, ctx: Dict[str, Any]) -> str:
        """
        Perform code morphing of text, then return resulting code

        :param src:
        :param ctx:
        :return:
        """
        chunks = []
        end = len(src)
        pos = 0
        while pos < end:
            match = cls.rx_open.search(src, pos)
            if not match:
                # No more instructions, stop
                chunks += [src[pos:]]
                break
            chunks += [src[pos : match.start()]]
            pos = match.end()
            cmatch = cls.rx_close.search(src, pos)
            if cmatch:
                idx = cmatch.start()
            else:
                idx = end
            reducer = getattr(cls, "reduce_%s" % match.group(1))
            nc = reducer(match.group(2), src[pos:idx], ctx)
            if nc:
                chunks += [nc]
            if cmatch:
                pos = cmatch.end()
            else:
                break
        return "\n".join(chunks)

    @classmethod
    def code_morph(cls, fn: Callable, ctx: Dict[str, Any]) -> Callable:
        src = inspect.getsource(fn)
        morphed_src = cls.code_morph_text(src, ctx)
        if morphed_src == src:
            return fn  # Not morphed
        return cls._compile(fn, morphed_src)

    @classmethod
    def _compile(cls, fn: Callable[..., Any], src: str):
        src = src.lstrip()
        key = hash_int(src)
        with cls.lock:
            mfn = cls.cache.get(key)
            if not mfn:
                code = compile(src, "<string>", "exec").co_consts[0]
                mfn = FunctionType(code, globals(), fn.__name__)
                cls.cache[key] = mfn
        return MethodType(mfn, fn.__self__)

    @classmethod
    def reduce_if(cls, expr: str, src: str, ctx: Dict[str, Any]) -> str:
        def q(m):
            s = m.group(0)
            if s.startswith(" in "):
                return s
            return ""

        # Evaluate condition
        cond = eval(expr, ctx)
        if not cond:
            return ""
        # Try to reduce next if
        if_match = cls.rx_if.match(src)
        if not if_match:
            return src
        next_cond = if_match.group(2).strip()
        if next_cond == expr:
            # Eliminate branch
            rest = src[if_match.end() :]
            return cls.dedent(rest)
        # reduce branch
        rx = re.compile("( ?and )?( in )?%s( and ?)?" % re.escape(expr), re.MULTILINE)
        next_cond = rx.sub(q, next_cond)
        return "%sif %s:\n%s" % (if_match.group(1), next_cond, src[if_match.end() :])

    @classmethod
    def dedent(cls, src: str):
        """
        Dedent sources 4 spaces left
        :param src:
        :return:
        """
        r = []
        to_dedent = True
        for line in src.splitlines():
            if to_dedent:
                if line.startswith("    "):
                    r += [line[4:]]
                    continue
                else:
                    to_dedent = False
            r += [line]
        if src.endswith("\n"):
            r += [""]
        return "\n".join(r)


code_morpher = CodeMorpher()
