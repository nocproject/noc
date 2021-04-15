# [liftbridge] section

Liftbridge service configuration

## addresses

|                |                            |
| -------------- | -------------------------- |
| Default value  | `liftbridge`               |
| YAML Path      | `liftbridge.addresses`     |
| Key-Value Path | `liftbridge/addresses`     |
| Environment    | `NOC_LIFTBRIDGE_ADDRESSES` |

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

## metrics_send_delay

Buffer collected metrics up to `metrics_send_delay` seconds.
Buffering reduces amount of liftbridge messages sent and
decreases overall system load by the price of increased
end-to-end delay between metric collection and persistent
storage in database.

|                |                                     |
| -------------- | ----------------------------------- |
| Default value  | `0.25`                              |
| YAML Path      | `liftbridge.metrics_send_delay`     |
| Key-Value Path | `liftbridge/metrics_send_delay`     |
| Environment    | `NOC_LIFTBRIDGE_METRICS_SEND_DELAY` |
