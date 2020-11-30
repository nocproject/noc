# [chwriter] section
Chwriter service configuration

## batch_size
Size of one portion from queue

Default value
:   50000

YAML Path
:   chwriter.batch_size

Key-Value Path
:   chwriter/batch_size

Environment
:   NOC_CHWRITER_BATCH_SIZE

## records_buffer
Own buffer of messages from queue

Default value
:   1000000

YAML Path
:   chwriter.records_buffer

Key-Value Path
:   chwriter/records_buffer

Environment
:   NOC_CHWRITER_RECORDS_BUFFER

## batch_delay_ms
Send every period time

Default value
:   10000

YAML Path
:   chwriter.batch_delay_ms

Key-Value Path
:   chwriter/batch_delay_ms

Environment
:   NOC_CHWRITER_BATCH_DELAY_MS

## channel_expire_interval
Close channel when no messages in this time

Default value
:   5M

YAML Path
:   chwriter.channel_expire_interval

Key-Value Path
:   chwriter/channel_expire_interval

Environment
:   NOC_CHWRITER_CHANNEL_EXPIRE_INTERVAL

## suspend_timeout_ms
How much time to sleep before continue

Default value
:   3000

YAML Path
:   chwriter.suspend_timeout_ms

Key-Value Path
:   chwriter/suspend_timeout_ms

Environment
:   NOC_CHWRITER_SUSPEND_TIMEOUT_MS

## topic
Topic in queue to listen to

Default value
:   chwriter

YAML Path
:   chwriter.topic

Key-Value Path
:   chwriter/topic

Environment
:   NOC_CHWRITER_TOPIC

## write_to

Default value
:   

YAML Path
:   chwriter.write_to

Key-Value Path
:   chwriter/write_to

Environment
:   NOC_CHWRITER_WRITE_TO

## max_in_flight
How many parts read simultaneously from queue

Default value
:   10

YAML Path
:   chwriter.max_in_flight

Key-Value Path
:   chwriter/max_in_flight

Environment
:   NOC_CHWRITER_MAX_IN_FLIGHT
