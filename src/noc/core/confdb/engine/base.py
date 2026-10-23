# ----------------------------------------------------------------------
# Predicate Engine
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import ast
import itertools
import types
import re
from collections import defaultdict

# NOC modules
from noc.core.vlan import has_vlan, optimize_filter
from noc.core.ip import IP
from noc.core.text import ranges_to_list
from .transformer import PredicateTransformer
from .var import Var
from ..db.base import ConfDB


def visitor(args):
    def wrap(f):
        f.visitor = args
        return f

    return wrap


class Engine:
    CLEANUP_NODES = {"hints"}

    def __init__(self) -> None:
        self.db = None

    def compile(self, expr):
        tree = ast.parse(expr, mode="eval")
        tree = PredicateTransformer(self).visit(tree)
        ast.fix_missing_locations(tree)
        return compile(tree, "<ast>", "eval")

    def _expr_to_python(self, expr):
        """Convert expression to python expression

        Args:
            expr
        """
        import astor

        tree = ast.parse(expr, mode="eval")
        tree = PredicateTransformer(self).visit(tree)
        ast.fix_missing_locations(tree)
        print(astor.to_source(tree))

    def query(self, expr, **kwargs):
        if not isinstance(expr, types.CodeType):
            expr = self.compile(expr)
        g = eval(expr, {}, {"self": self, "_input": self.iter_initial(**kwargs)})
        yield from g

    def any(self, expr, **kwargs):
        """Run query and return True if any result found

        Args:
            expr
            **kwargs
        """
        for _ in self.query(expr, **kwargs):
            return True
        return False

    def dump(self, format="tree"):
        return self.db.marshall(format)

    def insert_bulk(self, iter):
        if not self.db:
            self.db = ConfDB()
        self.db.insert_bulk(iter)

    def trim_and_append(self, path, value):
        """Trim all children nodes of path and append value

        Args:
            path: Tuple containing path
            value: iterable yielding path

        Returns:
            True if value replaced, False otherwise
        """
        current = self.db.db
        for p in path:
            current = current.find(p)
            if current is None:
                return False
        current.trim()
        current.insert(value)
        return True

    def find(self, *args):
        """Find node by path

        Args:
            *args: Path
        """
        assert self.db, "Database is not initialized"
        root = self.db.db
        return root.find_path(args)

    def rebase(self, src, dst):
        assert self.db, "Database is not initialized"
        root = self.db.db
        # Find source
        src_node = root.find_path(src)
        if not src_node:
            return
        # Ensure path to destination
        dst_node = root.insert(dst)
        # Merge node
        dst_node.merge_children(src_node.children)
        # Remove source node
        prev = root.find_path(src[:-1])
        del prev.children[src[-1]]

    def with_db(self, db):
        self.db = db
        return self

    def iter_product(self, _ctx, **kwargs):
        if kwargs:
            names = []
            params = []
            for k in kwargs:
                names.append(k)
                v = kwargs[k]
                if callable(v):
                    v = v(_ctx)
                if not isinstance(v, list):
                    v = [v]
                params.append(v)
            for values in itertools.product(*params):
                yield dict(zip(names, values))
        else:
            yield {}

    def iter_initial(self, **kwargs):
        yield from self.iter_product({}, **kwargs)

    @staticmethod
    def context_hash(ctx):
        return repr(ctx)

    @staticmethod
    def iter_unique(g):
        """Deduplicate generator

        Args:
            g
        """
        seen = set()
        for ctx in g:
            h = Engine.context_hash(ctx)
            if h not in seen:
                yield ctx
                seen.add(h)

    @staticmethod
    def resolve_var(ctx, v):
        """Resolve bound variable if necessary

        Args:
            ctx
            v
        """
        if isinstance(v, Var):
            return v.get(ctx)
        if callable(v):
            return v(ctx)
        return v

    def cleanup(self):
        """Remove temporary nodes"""
        assert self.db, "Database is not initialized"
        current = self.db.db
        if current.children:
            for c in self.CLEANUP_NODES:
                if c in current.children:
                    del current.children[c]

    def fn_Set(self, _input, **kwargs):
        """Set(k1=v1, ..., kN=vN)

        Modify context with additional variables. If v is list, apply all variables product.

        Args:
            _input
            **kwargs
        """

        def g():
            for ctx in _input:
                for pctx in self.iter_product(ctx, **kwargs):
                    nctx = ctx.copy()
                    nctx.update(pctx)
                    yield nctx

        # Deduplicate
        return self.iter_unique(g())

    def fn_Dump(self, _input, message=None):
        """Dump()
        Dump(message)
        Dump current context and pass unmodified

        Args:
            _input
            message
        """
        for ctx in _input:
            if message:
                print(f"{message}: {ctx!r}")
            else:
                print(ctx)
            yield ctx

    def fn_True(self, _input):
        """Pass context unmodified

        Args:
            _input
        """
        yield from _input

    def fn_False(self, _input):
        """Break predicate chain

        Args:
            _input
        """
        return iter(())

    def fn_Var(self, name):
        """Internal function referring to context variable

        Args:
            name
        """
        return Var(name)

    @visitor("vx")
    def fn_Sprintf(self, _input, name, fmt, *args):
        """
        Args:
            _input
            name
            fmt
            *args
        """
        assert isinstance(name, Var)
        for ctx in _input:
            nctx = ctx.copy()
            f = self.resolve_var(nctx, fmt)
            fmt_args = tuple(self.resolve_var(nctx, a) for a in args)
            name.set(nctx, f % fmt_args)
            yield nctx

    def fn_Match(self, _input, *args):
        """Match *args against database. Bind unbound variables on match

        Args:
            _input
            *args
        """

        def match_token(node, c, current, rest):
            f = node.find(current)
            if f is not None:
                if rest:  # Match tail
                    yield from match(f, c, rest)
                else:
                    yield c  # Final match

        def match_unbound(node, c, current, rest):
            for f in node.iter_nodes():
                nctx = c.copy()
                current.set(nctx, f.token)
                if rest:
                    yield from match(f, nctx, rest)
                else:
                    yield nctx

        def match(node, c, where):
            current = where[0]
            rest = where[1:]
            if isinstance(current, Var):
                if current.is_bound(c):
                    for wctx in match_token(node, c, current.get(c), rest):
                        yield wctx
                else:
                    for wctx in match_unbound(node, c, current, rest):
                        yield wctx
            else:
                for wctx in match_token(node, c, current, rest):
                    yield wctx

        assert self.db, "Current database is not set"
        for ctx in _input:
            yield from match(self.db.db, ctx, args)

    def fn_NotMatch(self, _input, *args):
        """Check *args is not in database. Bind unbound variables

        Args:
            _input
            *args
        """

        def not_match_token(node, c, current, rest):
            f = node.find(current)
            if rest:
                if f:  # Descent deeper
                    yield from not_match(f, c, rest)
                elif not any(True for x in rest if isinstance(x, Var) and not x.is_bound(c)):
                    # There is rest and token not found and no unbound variables left in rest
                    yield c
            elif not f:
                yield c  # Last token mismatch

        def not_match_unbound(node, c, current, rest):
            if rest:
                for f in node.iter_nodes():
                    uctx = c.copy()
                    current.set(uctx, f.token)
                    yield from not_match_token(node, uctx, f.token, rest)

        def not_match(node, c, where):
            current, rest = where[0], where[1:]
            if isinstance(current, Var):
                if current.is_bound(c):
                    for wctx in not_match_token(node, c, current.get(c), rest):
                        yield wctx
                else:
                    for wctx in not_match_unbound(node, c, current, rest):
                        yield wctx
            else:
                for wctx in not_match_token(node, c, current, rest):
                    yield wctx

        assert self.db, "Current database is not set"
        for ctx in _input:
            yield from not_match(self.db.db, ctx, args)

    def fn_Re(self, _input, pattern, name, ignore_case=None):
        """Match variable *name* against regular expression pattern.
        Pass context further if matched. If regular expression contains
        named groups, i.e. (?P<group_name>....), apply them as context variables

        Args:
            _input
            pattern
            name
        """
        flags = 0
        if ignore_case:
            flags |= re.IGNORECASE
        if isinstance(pattern, Var):
            rx = None
        else:
            rx = re.compile(pattern, flags)
        for ctx in _input:
            if isinstance(name, Var):
                value = name.get(ctx)
            else:
                value = name
            if not value:
                continue
            if rx:
                match = rx.search(value)
            else:
                match = re.search(pattern.get(ctx), value, flags)
            if match:
                groups = match.groupdict()
                if groups:
                    nctx = ctx.copy()
                    nctx.update(groups)
                    yield nctx
                else:
                    yield ctx

    def op_Not(self, g):
        """Context negation. Yields empty context if input is empty, Drops input otherwise

        Args:
            g
        """

        try:
            next(g)
        except StopIteration:
            yield {}

    def op_Or(self, _input, *args):
        # Split inputs
        inputs = itertools.tee(_input, len(args))
        # Make generators
        gens = [a(self, g) for a, g in zip(args, inputs)]
        return self.iter_unique(itertools.chain(*gens))

    def fn_Del(self, _input, *args):
        """Delete variables from context. Deduplicate contexts when necessary

        Args:
            _input
            *args: String or variable
        """

        def g():
            for ctx in _input:
                nctx = ctx.copy()
                for a in args:
                    if isinstance(a, Var):
                        name = a.name
                    else:
                        name = a
                    if name in nctx:
                        del nctx[name]
                yield nctx

        # Deduplicate
        return self.iter_unique(g())

    def fn_Fact(self, _input, *args):
        """Set Fact to database

        Args:
            _input
            *args: Path of fact, eigther constants or bound variables
        """
        assert self.db, "Current database is not set"
        for ctx in _input:
            self.db.insert([self.resolve_var(ctx, a) for a in args])
            yield ctx

    @visitor("xx")
    def fn_HasVLAN(self, _input, vlan_filter, vlan_id):
        """Check `vlan_id` is within `vlan_filter` expression

        Args:
            _input
            vlan_filter
            vlan_id
        """
        for ctx in _input:
            vf = self.resolve_var(ctx, vlan_filter)
            if not vf:
                continue
            vlan = self.resolve_var(ctx, vlan_id)
            if not vlan:
                continue
            if has_vlan(vf, vlan):
                yield ctx

    @visitor("xx")
    def fn_MatchAnyVLAN(self, _input, vlan_filter, vlans):
        """Check any `vlans` is within `vlan_filter` expression

        Args:
            _input
            vlan_filter
            vlans
        """
        for ctx in _input:
            vf = self.resolve_var(ctx, vlan_filter)
            if not vf:
                continue
            vf = set(ranges_to_list(vf))
            vs = self.resolve_var(ctx, vlans)
            if not vs:
                continue
            try:
                vs = set(ranges_to_list(str(vs)))
            except SyntaxError:
                return
            if vf.intersection(vs):
                yield ctx

    @visitor("xx")
    def fn_MatchAllVLAN(self, _input, vlan_filter, vlans):
        """Check all `vlans` is within `vlan_filter` expression

        Args:
            _input
            vlan_filter
            vlans
        """
        for ctx in _input:
            vf = self.resolve_var(ctx, vlan_filter)
            if not vf:
                continue
            vf = set(ranges_to_list(vf))
            vs = self.resolve_var(ctx, vlans)
            if not vs:
                continue
            try:
                vs = set(ranges_to_list(str(vs)))
            except SyntaxError:
                return
            if not vs - vf:
                yield ctx

    @visitor("xx")
    def fn_MatchExactVLAN(self, _input, vlan_filter, vlans):
        """Check all `vlans` is within `vlan_filter` expression

        Args:
            _input
            vlan_filter
            vlans
        """
        for ctx in _input:
            vf = self.resolve_var(ctx, vlan_filter)
            if not vf:
                continue
            vf = set(ranges_to_list(vf))
            vs = self.resolve_var(ctx, vlans)
            if not vs:
                continue
            try:
                vs = set(ranges_to_list(str(vs)))
            except SyntaxError:
                return
            if not vf.symmetric_difference(vs):
                yield ctx

    @visitor("xx")
    def fn_MatchPrefix(self, _input, prefix, address):
        """Check `address` is within prefix

        Args:
            _input
            prefix
            address
        """
        for ctx in _input:
            prefix = self.resolve_var(ctx, prefix)
            if not prefix:
                continue
            address = self.resolve_var(ctx, address)
            if not address:
                continue
            if address in IP.prefix(str(prefix)):
                yield ctx

    @visitor("x")
    def fn_Filter(self, _input, expr):
        """Pass context only if `expr` is evaluated as true

        Args:
            _input
            expr
        """
        for ctx in _input:
            if callable(expr):
                if not expr(ctx):
                    continue
            elif not expr:
                continue
            yield ctx

    def fn_Group(self, _input, *args, **kwargs):
        def update_context(g_ctx, new_ctx):
            if stack:
                for k in new_ctx:
                    if k in stack:
                        if k in g_ctx:
                            g_ctx[k].append(new_ctx[k])
                        else:
                            g_ctx[k] = [new_ctx[k]]
                    else:
                        g_ctx[k] = new_ctx[k]
            else:
                g_ctx.update(new_ctx)

        stack = kwargs.get("stack")
        # kwargs are callables, evaluate them
        if stack:
            stack = stack({})
        # Group
        contexts = {}
        for ctx in _input:
            kv = tuple(ctx.get(a) for a in args)
            if kv in contexts:
                update_context(contexts[kv], ctx)
            else:
                contexts[kv] = ctx
        # Yield
        for kv in sorted(contexts):
            yield contexts[kv]

    def _collapse_join(self, values, join):
        return join.join(values)

    def _collapse_joinrange(self, values, joinrange):
        return optimize_filter(joinrange.join(values))

    def fn_Collapse(self, _input, *args, **kwargs):
        """Collapse multiple keys to a single one following rules

        Args:
            _input
            *args
            **kwargs: One of collapse operation should be specified *
                join=<sep> -- join lines with separator sep
        """
        assert self.db, "Current database is not set"
        # Check operations
        op = None
        for k in kwargs:
            op = getattr(self, f"_collapse_{k}", None)
            if op:
                break
        assert op, "Collapse operation is not set"
        # kwargs are callables, evaluate them
        collapse_args = {k: kwargs[k]({}) for k in kwargs}
        # Group values
        match_args = [*list(args), Var("$value")]
        collected = defaultdict(list)  # path -> [value, ...]
        for ctx in self.fn_Match(_input, *match_args):
            path = tuple(self.resolve_var(ctx, p) for p in args)
            collected[path].append(ctx["$value"])
        # Apply changes
        for path in collected:
            # Merge values
            value = op(collected[path], **collapse_args)
            # Replace
            self.trim_and_append(path, [value])
        # Pass contexts unchanged
        yield from _input
