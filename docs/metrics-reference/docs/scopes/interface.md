---
uuid: a02a3a86-ee0e-4acc-b55f-026295d4db8e
---
# Interface Metric Scope

Interface-related metrics

## Data Table

ClickHouse Table: `interface`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `chassis` | {{ no }} | 
{{ tab }} `slot` | {{ no }} | 
{{ tab }} `module` | {{ no }} | 
{{ tab }} `port` | {{ no }} | 
{{ tab }} `unit` | {{ no }} | 
[broadcast_in](../types/interface/broadcast/in.md) | UInt64 | [Interface \| Broadcast \| In](../types/interface/broadcast/in.md)
[broadcast_out](../types/interface/broadcast/out.md) | UInt64 | [Interface \| Broadcast \| Out](../types/interface/broadcast/out.md)
[cinr](../types/radio/cinr.md) | Int16 | [Radio \| CINR](../types/radio/cinr.md)
[current_ma](../types/interface/dom/bias-current.md) | Int16 | [Interface \| DOM \| Bias Current](../types/interface/dom/bias-current.md)
[discards_in](../types/interface/discards/in.md) | UInt32 | [Interface \| Discards \| In](../types/interface/discards/in.md)
[discards_out](../types/interface/discards/out.md) | UInt32 | [Interface \| Discards \| Out](../types/interface/discards/out.md)
[errors_crc_in](../types/interface/errors/crc.md) | UInt32 | [Interface \| Errors \| CRC](../types/interface/errors/crc.md)
[errors_frame_in](../types/interface/errors/frame.md) | UInt32 | [Interface \| Errors \| Frame](../types/interface/errors/frame.md)
[errors_in](../types/interface/errors/in.md) | UInt32 | [Interface \| Errors \| In](../types/interface/errors/in.md)
[errors_in_delta](../types/interface/errors/in/delta.md) | UInt32 | [Interface \| Errors \| In \| Delta](../types/interface/errors/in/delta.md)
[errors_out](../types/interface/errors/out.md) | UInt32 | [Interface \| Errors \| Out](../types/interface/errors/out.md)
[errors_out_delta](../types/interface/errors/out/delta.md) | UInt32 | [Interface \| Errors \| Out \| Delta](../types/interface/errors/out/delta.md)
[load_in](../types/interface/load/in.md) | UInt64 | [Interface \| Load \| In](../types/interface/load/in.md)
[load_out](../types/interface/load/out.md) | UInt64 | [Interface \| Load \| Out](../types/interface/load/out.md)
[multicast_in](../types/interface/multicast/in.md) | UInt64 | [Interface \| Multicast \| In](../types/interface/multicast/in.md)
[multicast_out](../types/interface/multicast/out.md) | UInt64 | [Interface \| Multicast \| Out](../types/interface/multicast/out.md)
[noise_level](../types/radio/level/noise.md) | Int32 | [Radio \| Level \| Noise](../types/radio/level/noise.md)
[octets_in](../types/interface/octets/in.md) | UInt64 | [Interface \| Octets \| In](../types/interface/octets/in.md)
[octets_out](../types/interface/octets/out.md) | UInt64 | [Interface \| Octets \| Out](../types/interface/octets/out.md)
[optical_rx_dbm](../types/interface/dom/rxpower.md) | Int16 | [Interface \| DOM \| RxPower](../types/interface/dom/rxpower.md)
[optical_tx_dbm](../types/interface/dom/txpower.md) | Int16 | [Interface \| DOM \| TxPower](../types/interface/dom/txpower.md)
[packets_in](../types/interface/packets/in.md) | UInt64 | [Interface \| Packets \| In](../types/interface/packets/in.md)
[packets_out](../types/interface/packets/out.md) | UInt64 | [Interface \| Packets \| Out](../types/interface/packets/out.md)
[rf_tx_dbm](../types/interface/rf/txpower.md) | Float32 | [Interface \| RF \| TxPower](../types/interface/rf/txpower.md)
[rssi](../types/radio/rssi.md) | Int16 | [Radio \| RSSI](../types/radio/rssi.md)
[rx_power](../types/radio/rxpower.md) | Float32 | [Radio \| RxPower](../types/radio/rxpower.md)
[signal_level](../types/radio/level/signal.md) | Int32 | [Radio \| Level \| Signal](../types/radio/level/signal.md)
[speed](../types/interface/speed.md) | UInt64 | [Interface \| Speed](../types/interface/speed.md)
[status_admin](../types/interface/status/admin.md) | UInt8 | [Interface \| Status \| Admin](../types/interface/status/admin.md)
[status_duplex](../types/interface/status/duplex.md) | UInt8 | [Interface \| Status \| Duplex](../types/interface/status/duplex.md)
[status_oper](../types/interface/status/oper.md) | UInt8 | [Interface \| Status \| Oper](../types/interface/status/oper.md)
[temp_c](../types/interface/dom/temperature.md) | Int16 | [Interface \| DOM \| Temperature](../types/interface/dom/temperature.md)
[tx_power](../types/radio/txpower.md) | Int32 | [Radio \| TxPower](../types/radio/txpower.md)
[voltage_v](../types/interface/dom/voltage.md) | Int16 | [Interface \| DOM \| Voltage](../types/interface/dom/voltage.md)
[xdsl_line_attenuation_down](../types/interface/xdsl/line/attenuation/downstream.md) | UInt16 | [Interface \| xDSL \| Line \| Attenuation \| Downstream](../types/interface/xdsl/line/attenuation/downstream.md)
[xdsl_line_attenuation_up](../types/interface/xdsl/line/attenuation/upstream.md) | UInt16 | [Interface \| xDSL \| Line \| Attenuation \| Upstream](../types/interface/xdsl/line/attenuation/upstream.md)
[xdsl_line_errors_es_delta](../types/interface/xdsl/line/errors/es/delta.md) | UInt32 | [Interface \| xDSL \| Line \| Errors \| ES \| Delta](../types/interface/xdsl/line/errors/es/delta.md)
[xdsl_line_errors_lof_delta](../types/interface/xdsl/line/errors/lof/delta.md) | UInt32 | [Interface \| xDSL \| Line \| Errors \| LOF \| Delta](../types/interface/xdsl/line/errors/lof/delta.md)
[xdsl_line_errors_lols_delta](../types/interface/xdsl/line/errors/lols/delta.md) | UInt32 | [Interface \| xDSL \| Line \| Errors \| LOLS \| Delta](../types/interface/xdsl/line/errors/lols/delta.md)
[xdsl_line_errors_loss_delta](../types/interface/xdsl/line/errors/loss/delta.md) | UInt32 | [Interface \| xDSL \| Line \| Errors \| LOSS \| Delta](../types/interface/xdsl/line/errors/loss/delta.md)
[xdsl_line_errors_lprs_delta](../types/interface/xdsl/line/errors/lprs/delta.md) | UInt32 | [Interface \| xDSL \| Line \| Errors \| LPRS \| Delta](../types/interface/xdsl/line/errors/lprs/delta.md)
[xdsl_line_errors_retrain_delta](../types/interface/xdsl/line/errors/retrain/delta.md) | UInt32 | [Interface \| xDSL \| Line \| Errors \| Retrain \| Delta](../types/interface/xdsl/line/errors/retrain/delta.md)
[xdsl_line_errors_ses_delta](../types/interface/xdsl/line/errors/ses/delta.md) | UInt32 | [Interface \| xDSL \| Line \| Errors \| SES \| Delta](../types/interface/xdsl/line/errors/ses/delta.md)
[xdsl_line_errors_uas_delta](../types/interface/xdsl/line/errors/uas/delta.md) | UInt32 | [Interface \| xDSL \| Line \| Errors \| UAS \| Delta](../types/interface/xdsl/line/errors/uas/delta.md)
[xdsl_line_noise_margin_down](../types/interface/xdsl/line/noise-margin/downstream.md) | Int16 | [Interface \| xDSL \| Line \| Noise Margin \| Downstream](../types/interface/xdsl/line/noise-margin/downstream.md)
[xdsl_line_noise_margin_up](../types/interface/xdsl/line/noise-margin/upstream.md) | Int16 | [Interface \| xDSL \| Line \| Noise Margin \| Upstream](../types/interface/xdsl/line/noise-margin/upstream.md)
[xdsl_line_snr_down](../types/interface/xdsl/line/snr/downstream.md) | UInt16 | [Interface \| xDSL \| Line \| SNR \| Downstream](../types/interface/xdsl/line/snr/downstream.md)
[xdsl_line_snr_up](../types/interface/xdsl/line/snr/upstream.md) | UInt16 | [Interface \| xDSL \| Line \| SNR \| Upstream](../types/interface/xdsl/line/snr/upstream.md)
[xdsl_line_txpower_down](../types/interface/xdsl/line/txpower/downstream.md) | UInt16 | [Interface \| xDSL \| Line \| TxPower \| Downstream](../types/interface/xdsl/line/txpower/downstream.md)
[xdsl_line_txpower_up](../types/interface/xdsl/line/txpower/upstream.md) | UInt16 | [Interface \| xDSL \| Line \| TxPower \| Upstream](../types/interface/xdsl/line/txpower/upstream.md)
