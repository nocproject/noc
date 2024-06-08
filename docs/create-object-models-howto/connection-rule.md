# Connection Rules

Connection rules are used to transform a linear list of objects returned by the `get_inventory` script into a tree structure by organizing the appropriate connections.

| Attribute                   | Type       | Description                                                                                                                                                                                                                                      |
| --------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| name                        | String     | Rule name                                                                                                                                                                                                                                        |
| is_builtin                  | Boolean    | Flag indicating synchronization with the distribution                                                                                                                                                                                            |
| description                 | String     | Description                                                                                                                                                                                                                                      |
| context                     | List       | Description of contexts                                                                                                                                                                                                                          |
| {{ tab }} type              | String     | Object type (returned by `get_inventory`)                                                                                                                                                                                                        |
| {{ tab }} scope             | String     | The name of the scope type associated with this type                                                                                                                                                                                             |
| {{ tab }} reset_scopes      | StringList | A list of scope names that need to be reset                                                                                                                                                                                                      |
| rules {{ complex }}         | ListObject | List of rules                                                                                                                                                                                                                                    |
| {{ tab }} match_type        | String     | The type for which the rule is applicable                                                                                                                                                                                                        |
| {{ tab }} match_connection  | String     | The name of the connection to be linked with another object when the rule is triggered. Variables from the context may be included in the name within curly braces (e.g., {variable})                                                            |
| {{ tab }} scope             | String     | The scope in which the match is performed. By default, the search is performed from the current object to the end of the list of get_inventory objects. If the scope name starts with a minus sign (-), the search is performed in reverse order |
| {{ tab }} target_type       | String     | The type of the object to connect with the current object                                                                                                                                                                                        |
| {{ tab }} target_number     | String     | If specified, the object is connected not to the first one encountered but to the one with a specific number                                                                                                                                     |
| {{ tab }} target_connection | String     | The name of the connection on the other side to be linked when the rule is triggered. Variables from the context may be included in the name within curly braces (e.g., {variable})                                                              |

## Algorithm for Finding Matches:

For each object from `get_inventory`:

* For all rules where match_type matches the object type:
    * If the scope starts with a minus sign (-), search from the current object to the beginning of the object list; otherwise, search from the current object to the end. Find an object with a type matching target_type. If target_number is specified, check the object number as well. The scope variable in the context must match.
    * If we find an object:
        * Expand the names match_connection and target_connection.
        * If the corresponding connections exist on both objects, connect them, and move on to the next object.
    * Check the next rule.

## Examples

A switch with `sfp`, and the `sfp` modules should be connected to the chassis using the `connection` `GiX_sfp`, where `X` is the port number.

Output from `get_inventory`:

| Type    | Number |
| ------- | ------ |
| CHASSIS | 1      |
| XCVR    | 25     |
| XCVR    | 26     |

Context settings:

| Type    | Scope   | Reset Scope |
| ------- | ------- | ----------- |
| CHASSIS | chassis |             |

Rules:

| match_type | match_connection | scope   | target_type | target_number | target_connection |
| ---------- | ---------------- | ------- | ----------- | ------------- | ----------------- |
| XCVR       | in               | chassis | CHASSIS     |               | Gi{N}_sfp         |

On the first pass through the list of objects, the following context values will be generated:

| Type    | Number | Context        |
| ------- | ------ | -------------- |
| CHASSIS | 1      | chassis=1,N=1  |
| XCVR    | 25     | chassis=1,N=25 |
| XCVR    | 26     | chassis=1,N=26 |

As a result, the rule will trigger for the transceivers, and the following connections will be created:

| Type    | connection | Type      | connection |
| ------- | ---------- | --------- | ---------- |
| XCVR 25 | in         | CHASSIS 1 | Gi25_sfp   |
| XCVR 26 | in         | CHASSIS 1 | Gi26_sfp   |
