# [nsqd] section
Nsqd service configuration

## addresses

Default value
:   service="nsqd", wait=True, near=True, full_result=False

YAML Path
:   nsqd.addresses

Key-Value Path
:   nsqd/addresses

Environment
:   NOC_NSQD_ADDRESSES

## http_addresses

Default value
:   service="nsqdhttp", wait=True, near=True, full_result=False

YAML Path
:   nsqd.http_addresses

Key-Value Path
:   nsqd/http_addresses

Environment
:   NOC_NSQD_HTTP_ADDRESSES

## pub_retries

Default value
:   5

YAML Path
:   nsqd.pub_retries

Key-Value Path
:   nsqd/pub_retries

Environment
:   NOC_NSQD_PUB_RETRIES

## pub_retry_delay

Default value
:   1.0

YAML Path
:   nsqd.pub_retry_delay

Key-Value Path
:   nsqd/pub_retry_delay

Environment
:   NOC_NSQD_PUB_RETRY_DELAY

## mpub_messages

Default value
:   10000

YAML Path
:   nsqd.mpub_messages

Key-Value Path
:   nsqd/mpub_messages

Environment
:   NOC_NSQD_MPUB_MESSAGES

## mpub_size

Default value
:   1048576

YAML Path
:   nsqd.mpub_size

Key-Value Path
:   nsqd/mpub_size

Environment
:   NOC_NSQD_MPUB_SIZE

## topic_mpub_rate

Default value
:   10

YAML Path
:   nsqd.topic_mpub_rate

Key-Value Path
:   nsqd/topic_mpub_rate

Environment
:   NOC_NSQD_TOPIC_MPUB_RATE

## ch_chunk_size

Default value
:   4000

YAML Path
:   nsqd.ch_chunk_size

Key-Value Path
:   nsqd/ch_chunk_size

Environment
:   NOC_NSQD_CH_CHUNK_SIZE

## connect_timeout

Default value
:   3s

YAML Path
:   nsqd.connect_timeout

Key-Value Path
:   nsqd/connect_timeout

Environment
:   NOC_NSQD_CONNECT_TIMEOUT

## request_timeout

Default value
:   30s

YAML Path
:   nsqd.request_timeout

Key-Value Path
:   nsqd/request_timeout

Environment
:   NOC_NSQD_REQUEST_TIMEOUT

## reconnect_interval

Default value
:   15

YAML Path
:   nsqd.reconnect_interval

Key-Value Path
:   nsqd/reconnect_interval

Environment
:   NOC_NSQD_RECONNECT_INTERVAL

## compression

Default value
:   

Possible values
:
* 
* deflate
* snappy

YAML Path
:   nsqd.compression

Key-Value Path
:   nsqd/compression

Environment
:   NOC_NSQD_COMPRESSION

## compression_level

Default value
:   6

YAML Path
:   nsqd.compression_level

Key-Value Path
:   nsqd/compression_level

Environment
:   NOC_NSQD_COMPRESSION_LEVEL

## max_in_flight

Default value
:   1

YAML Path
:   nsqd.max_in_flight

Key-Value Path
:   nsqd/max_in_flight

Environment
:   NOC_NSQD_MAX_IN_FLIGHT
