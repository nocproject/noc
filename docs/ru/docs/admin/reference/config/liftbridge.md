# [liftbridge] section

Liftbridge service configuration

## addresses

|                |                                                                 |
| -------------- | --------------------------------------------------------------- |
| Default value  | `service="liftbridge", wait=True, near=True, full_result=False` |
| YAML Path      | `liftbridge.addresses`                                          |
| Key-Value Path | `liftbridge/addresses`                                          |
| Environment    | `NOC_LIFTBRIDGE_ADDRESSES`                                      |

## max_message_size

Max message size for GRPC client

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `-1`                              |
| YAML Path      | `liftbridge.max_message_size`     |
| Key-Value Path | `liftbridge/max_message_size`     |
| Environment    | `NOC_LIFTBRIDGE_MAX_MESSAGE_SIZE` |

## publish_async_ack_timeout

|                |                                            |
| -------------- | ------------------------------------------ |
| Default value  | `10`                                       |
| YAML Path      | `liftbridge.publish_async_ack_timeout`     |
| Key-Value Path | `liftbridge/publish_async_ack_timeout`     |
| Environment    | `NOC_LIFTBRIDGE_PUBLISH_ASYNC_ACK_TIMEOUT` |
