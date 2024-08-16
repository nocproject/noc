# Object Models

Object model is the definition of inventory object's behavior.

| Name                      | Type                          | Description                                                                                                                                                                                                                         |
| ------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                    | String                        | Model name                                                                                                                                                                                                                          |
| `description`             | String                        | Model description                                                                                                                                                                                                                   |
| `vendor`                  | Reference                     | [Vendor](../../user/reference/concepts/vendor/index.md) reference                                                                                                                                                                   |
| `data`                    | Object                        | Model attributes, refer to [Model Interface](model-interface/index.md)                                                                                                                                                              |
| `connections`             | Array of Object {{ complex }} | Possible connections                                                                                                                                                                                                                |
| {{ tab }} `name`          | String                        | Unique connection name                                                                                                                                                                                                              |
| {{ tab }} `description`   | String                        | Connection description                                                                                                                                                                                                              |
| {{ tab }} `type`          | Reference                     | [Connection Type](connection-type.md) reference                                                                                                                                                                                     |
| {{ tab }} `direction`     | String                        | Connection direction (See [Direction Discussion](connection-restrictions.md#direction) for details):                                                                                                                             |
|                           |                               | `i` - internal. Connected object will be placed inside this object.                                                                                                                                                                 |
|                           |                               | `o` - outside. This object will be placed inside connected one.                                                                                                                                                                     |
|                           |                               | `s` - side connection. Neither objects will be placed inside each other.                                                                                                                                                            |
| {{ tab }} `gender`        | String                        | Connection gender (See [Connection Gender Discussion](connection-restrictions.md#gender) for details)                                                                                                                            |
|                           |                               | `m` - male                                                                                                                                                                                                                          |
|                           |                               | `f` - female                                                                                                                                                                                                                        |
|                           |                               | `s` - genderless, side connection                                                                                                                                                                                                   |
| {{ tab }} `protocols`     | Array of String               | Optional list of protocols, supported on given connection. See [Inventory Protocols](inventory-protocols.md) for reference and [Protocols Discussion](connection-restrictions.md#protocols) for details.        |
| {{ tab }} `group`         | String                        | Crossing group (See [Group Discussion](connection-restrictions.md#groups) for details)                                                                                                                                           |
| {{ tab }} `cross`         | String                        | Internal connection crossing (See [Cross Discussion](connection-restrictions.md#cross) for details                                                                                                              |
| {{ tab }} `internal_name` | String                        | Optional internal name. May be used in Connection Rules {{ wbr }} along with `name`, but not shown in user interface. {{ wbr }} May be used to hide long names, {{ wbr }} like PCIe identifiers and to replace {{ wbr }} them to short and clear names. |