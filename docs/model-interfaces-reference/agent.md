# agent model interface

`agent` interface stores NOC Agent bindings

## Variables
<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `is_agent` | bool | Object can be bind to the Agent | {{ no }} | {{ yes }} |
| `agent` | objectid | Agent id | {{ no }} | {{ no }} |

<!-- table end -->

## Examples

``` json
{
    "agent": {
        "is_agent": true,
        "agent_id": "123456789012345678901234"
    }
}
```