# container Model Interface

Denotes *Container* as an object capable of holding another object,
bypassing *Connections*. Containers may represent logical groups,
such as *Countries* or *Cities* and physical entries, like
*Points of Precence*, *Rooms* or *Racks*.

Objects holding in *Container* reference to container via *Object.container*
field. Following rules are applied:

* When object being placed to container (having .container field set),
  all its *Connections* with *o* direction are released
* When object beeing connected to other object using *o* direction connection,
  its been withdraw from container (having .container field reset)

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `container` | bool | Object is container (can hold another objects) | {{ yes }} | {{ yes }} |

<!-- table end -->

## Examples

```json
{
  "container": {
    "container": true
  }
}
```
