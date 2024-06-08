# Handler

<!-- prettier-ignore -->
!!! note
    `Handlers` are advanced topic which may require basic
    or deeper knowledge of Python language

NOC Plugin ecosystem bases on `Handlers` - the Python functions which
allow to customize NOC behavior. NOC offers a lot of hooks where the
custom code can be injected to alter default behaviour. Refer to
[Handlers Overview](../../handlers-reference/index.md) for possible handlers and examples

## Naming Conventions

`Handler` is mere a string like:

```
noc.custom.config.filters.MyFilter3
```

Prefix `noc` means handler refers to one of NOCs modules (either
builtin, pyRule or Custom). It's possible to use other prefixes, say
for third-party python modules not integrated to NOC directly.
`MyFilter3` is the function (or other callable) name in python module
`noc.custom.config.filters`.

## Built-in

Built-in handlers are provided along with NOC distribution. i.e.
`noc.fm.handlers.event.link.oper_up` refers to function `oper_up` in file:

```
<NOC root>
+-> fm
  +-> handlers
      +-> event
          +-> link.py
```

Built-in handlers usually used in event and alarm classes.

## Custom

Custom handlers are attached to NOC with `custom` repo. Custom handlers
are distinguished by `noc.custom` prefix. i.e.
`noc.custom.handlers.config.filters.MyFilter refers to function`MyFilter`
from file:

```
<NOC custom root>
+-> handlers
    +-> config
        +-> filters.py
```

You need to deploy custom repo in order to use custom handlers.

## PyRules

PyRules are custom Python modules stored in NOC database. PyRule handlers
are distinguished by `noc.pyrules` prefix. i.e
`noc.pyrules.config.filters.MyPyRuleFilter` refers to `MyPyRuleFilter`
function from PyRule named `config.filters`
