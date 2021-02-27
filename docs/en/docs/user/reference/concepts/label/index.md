# Label

`Labels` are user-defined "Tags" which can be attached virtually to any data
in NOC. Labels can hold additional configuration:

- Visual Appearance.
- Application area, i.e. to which kinds of entities they can be attached to.
- Exposition rules.
- Protection flag.

## Scoped Labels

Labels can be groupped to the scopes. Only one label from scope may be attached
to single entity. Scopes are separated by `::` sign. Scopes can be nested.
Examples of scoped labels:

- `myscope::mylabel`
- `myscope::mysubscope::mylabel`

## Effective Labels

Labels are combined with group settings to build `Effective Labels`. Effective
labels contain directly set labels enriched with inherited ones.

Inheritance order is in the table below. For the scoped labels, leftmost
entry is preferable. Some kinds of inheritance have an exposition restrictions.

| Entity                | Inheritance Order                                             | Exposition Restrictions |
| --------------------- | ------------------------------------------------------------- | ----------------------- |
| Agent                 | Agent, Agent Profile                                          |                         |
| Service               | Service, Service Profile, Service Parent                      |                         |
| Коллектор агента      | Service, Agent                                                | `expose_metric`         |
| Administrative Domain | Administrative Domain, Administrative Domain Parent           |                         |
| Managed Object        | Managed Object, Managed Object Profile, Administrative Domain | `expose_managed_object` |
| Alarm                 | Alarm, Interface, Managed Object                              | `expose_alarm`          |
| Interface             | Interface, Interface Profile, Managed Object                  | `expose_interface`      |

## Protected Labels

Protected labels may be applied only to group settings and cannot be placed
to final entities manually.

## Wildcard Labels

Wildcard labels are used in the match operations and specify all labels
from given scope and all nested scopes. Wildcards are combined from scope
followed by `*` sign. Examples:

- `myscope::*`
- `myscope::mysubscope::*`
