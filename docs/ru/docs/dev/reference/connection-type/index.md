# Connection Types

Connection types define inventory connection restrictions: physical shape
of the connection, number size and placement of the pins and the
additional vendor-defined restrictions. See
[Connection Type Discussion](../../background/connection-restrictions/index.md#type)
for the detailed explanation.

| Name        | Type            | Description                                                                                                                                                         |
| ----------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| name        | String          | Connection type name                                                                                                                                                |
| description | String          | Optional description                                                                                                                                                |
| extend      | Reference       | Optional parent type reference. See [Type Inheritance Discussion](../../background/connection-type-restrictions/index.md#inheritance) for the detailed explanation. |
| genders     | String          | Possible genders combination. See [Gender Restriction](../../background/connection-type-restrictions/index.md#gender-restrictions) for the detailed explanation.    |
|             |                 | &bull; `s` - symmetric, genderless same type connection                                                                                                             |
|             |                 | &bull; `ss` - symmetric, genderless same type connection. More than two objects may be connected                                                                    |
|             |                 | &bull; `m` - only male types, compatible female types are selected via `c_groups`                                                                                   |
|             |                 | &bull; `f` - only female types, compatible male types are selected via `c_groups`                                                                                   |
|             |                 | &bull; `mf` - male and female types                                                                                                                                 |
|             |                 | &bull; `mmf` - one or more male may be connected to one female                                                                                                      |
|             |                 | &bull; `mff` - two or one females may be connected to one male                                                                                                      |
| data        | Object          | Model attributes, refer to [Model Interface](../model-interface/index.md)                                                                                           |
| c_group     | Array of String | Additional compatible connection types [Gender Restriction](../../background/connection-type-restrictions/index.md#cgroups) for the detailed explanation.           |
| matchers    | Array of Object |                                                                                                                                                                     |
