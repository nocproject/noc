# Interface

Interface-related metrics

## Table Structure
The `Interface` metric scope is stored
in the `interface` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |
| service | sa.Service |
| cpe | inv.CPE |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::chassis::*` | chassis |  |
| `noc::slot::*` | slot |  |
| `noc::module::*` | module |  |
| `noc::interface::*` |  | interface |
| `noc::subinterface::*` |  | subinterface |
| `noc::queue::*` |  | queue |
| `noc::traffic_class::*` |  | traffic_class |
| `noc::tos::*` |  | tos |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="interface-broadcast-in"></a>broadcast_in | UInt64 | Interface \| Broadcast \| In | Broadcast packets on input interface | packet/s | pps | 1 |
| <a id="interface-broadcast-out"></a>broadcast_out | UInt64 | Interface \| Broadcast \| Out | Broadcast packets on output interface | packet/s | pps | 1 |
| <a id="interface-cbqos-drops-in-delta"></a>cbqos_drops_in_delta | UInt64 | Interface \| CBQOS \| Drops \| In \| Delta | Drops packet on input class-map (delta) | packets | pkt | 1 |
| <a id="interface-cbqos-drops-out-delta"></a>cbqos_drops_out_delta | UInt64 | Interface \| CBQOS \| Drops \| Out \| Delta | Drops packet on output class-map (delta) | packets | pkt | 1 |
| <a id="interface-cbqos-octets-in-delta"></a>cbqos_octets_in_delta | UInt64 | Interface \| CBQOS \| Octets \| In \| Delta | The total number of received octets passed by the interface class-map. | bytes | byte | 1 |
| <a id="interface-cbqos-octets-out-delta"></a>cbqos_octets_out_delta | UInt64 | Interface \| CBQOS \| Octets \| Out \| Delta | The total number of sending octets passed by the interface class-map. | bytes | byte | 1 |
| <a id="interface-cbqos-packets-in-delta"></a>cbqos_packets_in_delta | UInt64 | Interface \| CBQOS \| Packets \| In \| Delta | The total number of received packets passed by the interface class-map. | bytes | pkt | 1 |
| <a id="interface-cbqos-packets-out-delta"></a>cbqos_packets_out_delta | UInt64 | Interface \| CBQOS \| Packets \| Out \| Delta | The total number of sending packets passed by the interface class-map. | bytes | pkt | 1 |
| <a id="radio-cinr"></a>cinr | Int16 | Radio \| CINR | Carrier to Interference + Noise Ratio | dB | dB | 1 |
| <a id="interface-dom-bias-current"></a>current_ma | Int16 | Interface \| DOM \| Bias Current | Laser bias current | mA | A | m |
| <a id="interface-discards-in"></a>discards_in | UInt32 | Interface \| Discards \| In | Discard packet on input interface | packet/s | pps | 1 |
| <a id="interface-discards-out"></a>discards_out | UInt32 | Interface \| Discards \| Out | Discard packet on output interface | packet/s | pps | 1 |
| <a id="interface-errors-collision-delta"></a>errors_collision_delta | UInt64 | Interface \| Errors \| Collision \| Delta | The number of output collisions detected on this interface. Delta | None | 1 | 1 |
| <a id="interface-errors-collision-rate"></a>errors_collision_rate | UInt32 | Interface \| Errors \| Collision \| Rate | The number of output collisions detected on this interface. Rate | None | rate | 1 |
| <a id="interface-errors-crc"></a>errors_crc_in | UInt64 | Interface \| Errors \| CRC | Errors when recieved packets which have CRC checking errors  | None | pkt | 1 |
| <a id="interface-errors-crc-delta"></a>errors_crc_in_delta | UInt64 | Interface \| Errors \| CRC \| Delta | Errors when recieved packets which have CRC checking errors Delta | None | pkt | 1 |
| <a id="interface-errors-frame"></a>errors_frame_in | UInt32 | Interface \| Errors \| Frame | Errors when received frames whose actual length differs with 802.3  | packet/s | pps | 1 |
| <a id="interface-errors-frame-delta"></a>errors_frame_in_delta | UInt32 | Interface \| Errors \| Frame \| Delta | Errors when received frames whose actual length differs with 802.3 Delta | None | 1 | 1 |
| <a id="interface-errors-in"></a>errors_in | UInt32 | Interface \| Errors \| In | Errors when receive packet | packet/s | pps | 1 |
| <a id="interface-errors-in-delta"></a>errors_in_delta | UInt32 | Interface \| Errors \| In \| Delta | Errors when receive packet (delta) | packets | pkt | 1 |
| <a id="interface-errors-out"></a>errors_out | UInt32 | Interface \| Errors \| Out | Errors when transmit packet | packet/s | pps | 1 |
| <a id="interface-errors-out-delta"></a>errors_out_delta | UInt32 | Interface \| Errors \| Out \| Delta | Errors when transmit packet (delta) | packets | pkt | 1 |
| <a id="interface-last-change"></a>lastchange | Int16 | Interface \| Last Change | Last change interface day(s) | day(s) | 1 | 1 |
| <a id="interface-load-in"></a>load_in | UInt64 | Interface \| Load \| In | Interface input throughput | bit/s | bit/s | 1 |
| <a id="interface-load-out"></a>load_out | UInt64 | Interface \| Load \| Out | Interface output throughput | bit/s | bit/s | 1 |
| <a id="radio-mcs"></a>mcs | Int8 | Radio \| MCS | Modulation Coding Scheme | None | 1 | 1 |
| <a id="interface-multicast-in"></a>multicast_in | UInt64 | Interface \| Multicast \| In | Multicast packets on input interface | packet/s | pps | 1 |
| <a id="interface-multicast-in-delta"></a>multicast_in_delta | UInt64 | Interface \| Multicast \| In \| Delta | Multicast packets on input interface Delta | None | 1 | 1 |
| <a id="interface-multicast-out"></a>multicast_out | UInt64 | Interface \| Multicast \| Out | Multicast packets on output interface | packet/s | pps | 1 |
| <a id="radio-level-noise"></a>noise_level | Int32 | Radio \| Level \| Noise | Noise Level | dBm | dBm | 1 |
| <a id="interface-octets-in"></a>octets_in | UInt64 | Interface \| Octets \| In | The total number of octets received on the interface, including framing characters.  | bytes | byte | 1 |
| <a id="interface-octets-in-delta"></a>octets_in_delta | UInt32 | Interface \| Octets \| In \| Delta | Delta for total number of octets received on the interface, including framing characters. | bytes | byte | 1 |
| <a id="interface-octets-out"></a>octets_out | UInt64 | Interface \| Octets \| Out | The total number of octets transmitted out of the interface, including framing characters. | bytes | byte | 1 |
| <a id="interface-octets-out-delta"></a>octets_out_delta | UInt32 | Interface \| Octets \| Out \| Delta | Delta for total number of octets transmitted out of the interface, including framing characters. | bytes | byte | 1 |
| <a id="interface-dom-errors-bip-downstream"></a>optical_errors_bip_ds | UInt32 | Interface \| DOM \| Errors \| BIP \| Downstream | Indicates the count of downstream frame bit-interleaved parity (BIP) errors | None | 1 | 1 |
| <a id="interface-dom-errors-bip-downstream-delta"></a>optical_errors_bip_ds_delta | UInt32 | Interface \| DOM \| Errors \| BIP \| Downstream \| Delta | Indicates the count of downstream frame bit-interleaved parity (BIP) errors | None | 1 | 1 |
| <a id="interface-dom-errors-bip-upstream"></a>optical_errors_bip_us | UInt32 | Interface \| DOM \| Errors \| BIP \| Upstream | Indicates the count of upstream frame bit-interleaved parity (BIP) errors | None | 1 | 1 |
| <a id="interface-dom-errors-bip-upstream-delta"></a>optical_errors_bip_us_delta | UInt32 | Interface \| DOM \| Errors \| BIP \| Upstream \| Delta | Indicates the count of upstream frame bit-interleaved parity (BIP) errors | None | 1 | 1 |
| <a id="interface-dom-errors-hec-upstream"></a>optical_errors_hec_us | UInt32 | Interface \| DOM \| Errors \| HEC \| Upstream | Indicates the count of upstream frame header error control (HEC) | None | 1 | 1 |
| <a id="interface-dom-errors-hec-upstream-delta"></a>optical_errors_hec_us_delta | UInt32 | Interface \| DOM \| Errors \| HEC \| Upstream \| Delta | Indicates the count of upstream frame header error control (HEC) | None | 1 | 1 |
| <a id="interface-dom-laser-status"></a>optical_laser_status | Int8 | Interface \| DOM \| Laser status | None | s | 1 | 1 |
| <a id="interface-dom-rxpower"></a>optical_rx_dbm | Int16 | Interface \| DOM \| RxPower | Signal Receive Power on transmitter | dBm | dBm | 1 |
| <a id="interface-dom-txpower"></a>optical_tx_dbm | Int16 | Interface \| DOM \| TxPower | Signal Transmit Power on transmitter | dBm | dBm | 1 |
| <a id="interface-packets-in"></a>packets_in | UInt64 | Interface \| Packets \| In | Packets on input interface | packet/s | pps | 1 |
| <a id="interface-packets-out"></a>packets_out | UInt64 | Interface \| Packets \| Out | Packets on output interface | packet/s | pps | 1 |
| <a id="interface-qos-discards-in-delta"></a>qos_discards_in_delta | UInt64 | Interface \| QOS \| Discards \| In \| Delta | Discards packet on input queue (delta) | packets | pkt | 1 |
| <a id="interface-qos-discards-out-delta"></a>qos_discards_out_delta | UInt64 | Interface \| QOS \| Discards \| Out \| Delta | Discards packet on output queue (delta) | packets | pkt | 1 |
| <a id="interface-qos-octets-in"></a>qos_octets_in | UInt64 | Interface \| QOS \| Octets \| In | The total number of received octets passed by the interface queue. | bytes | byte | 1 |
| <a id="interface-qos-octets-out"></a>qos_octets_out | UInt64 | Interface \| QOS \| Octets \| Out | The total number of transmitted out octets passed by the interface queue. | bytes | byte | 1 |
| <a id="interface-qos-packets-in"></a>qos_packets_in | UInt64 | Interface \| QOS \| Packets \| In | Packets on input interface queue | packet/s | pps | 1 |
| <a id="interface-qos-packets-out"></a>qos_packets_out | UInt64 | Interface \| QOS \| Packets \| Out | Packets on output interface queue | packet/s | pps | 1 |
| <a id="interface-rf-txpower"></a>rf_tx_dbm | Float32 | Interface \| RF \| TxPower | RF Tx power | dBuV | dBm | 1 |
| <a id="radio-rssi"></a>rssi | Int16 | Radio \| RSSI | Received signal strength indicator | dBm | dBm | 1 |
| <a id="radio-rxpower"></a>rx_power | Float32 | Radio \| RxPower | Signal Rx Power on transmitter | dBm | dBm | 1 |
| <a id="radio-level-signal"></a>signal_level | Int32 | Radio \| Level \| Signal | Signal Level | dBm | dBm | 1 |
| <a id="interface-speed"></a>speed | UInt64 | Interface \| Speed | Interface speed | bit/s | bit/s | 1 |
| <a id="interface-status-admin"></a>status_admin | UInt8 | Interface \| Status \| Admin | Interface admin state |  | ifaceoper | 1 |
| <a id="interface-status-duplex"></a>status_duplex | UInt8 | Interface \| Status \| Duplex | Interface duplex status (1 - unknown, 2 - half, 3 - full) |  | ifaceduplex | 1 |
| <a id="interface-status-oper"></a>status_oper | UInt8 | Interface \| Status \| Oper | Interface admin status |  | ifaceoper | 1 |
| <a id="interface-dom-temperature"></a>temp_c | Int16 | Interface \| DOM \| Temperature | Temparature, in Celsius | C | C | 1 |
| <a id="radio-txpower"></a>tx_power | Int32 | Radio \| TxPower | Signal Tx Power on transmitter | dBm | dBm | 1 |
| <a id="interface-dom-voltage"></a>voltage_v | Int16 | Interface \| DOM \| Voltage | Transceiver supply voltage | V | VDC | 1 |
| <a id="interface-xdsl-line-attenuation-downstream"></a>xdsl_line_attenuation_down | UInt16 | Interface \| xDSL \| Line \| Attenuation \| Downstream | Measured difference in the the total power transmitted by this ATU and total power received by the peer ATU. | dB | dB | 1 |
| <a id="interface-xdsl-line-attenuation-upstream"></a>xdsl_line_attenuation_up | UInt16 | Interface \| xDSL \| Line \| Attenuation \| Upstream | Measured difference in the total power transmitted by the peer ATU and the total power received by this ATU. | dB | dB | 1 |
| <a id="interface-xdsl-line-errors-es-delta"></a>xdsl_line_errors_es_delta | UInt32 | Interface \| xDSL \| Line \| Errors \| ES \| Delta | Count of the number of Errored Seconds since agent reset.  The errored second parameter is a count of one-second intervals containing one or more crc anomalies, or one or more los or sef defects. | count | 1 | 1 |
| <a id="interface-xdsl-line-errors-lof-delta"></a>xdsl_line_errors_lof_delta | UInt32 | Interface \| xDSL \| Line \| Errors \| LOF \| Delta | Count of the number of Loss of Framing failures since agent reset. | count | 1 | 1 |
| <a id="interface-xdsl-line-errors-lols-delta"></a>xdsl_line_errors_lols_delta | UInt32 | Interface \| xDSL \| Line \| Errors \| LOLS \| Delta | Count of the number of Loss of Link failures since agent reset. | count | 1 | 1 |
| <a id="interface-xdsl-line-errors-loss-delta"></a>xdsl_line_errors_loss_delta | UInt32 | Interface \| xDSL \| Line \| Errors \| LOSS \| Delta | Count of the number of Loss of Signal failures since agent reset. | count | 1 | 1 |
| <a id="interface-xdsl-line-errors-lprs-delta"></a>xdsl_line_errors_lprs_delta | UInt32 | Interface \| xDSL \| Line \| Errors \| LPRS \| Delta | Count of the number of Loss of Power failures since agent reset. | count | 1 | 1 |
| <a id="interface-xdsl-line-errors-retrain-delta"></a>xdsl_line_errors_retrain_delta | UInt32 | Interface \| xDSL \| Line \| Errors \| Retrain \| Delta | Refer to changing the line parameters (retrain) to adapt to the change of transmission line characteristics. | count | 1 | 1 |
| <a id="interface-xdsl-line-errors-ses-delta"></a>xdsl_line_errors_ses_delta | UInt32 | Interface \| xDSL \| Line \| Errors \| SES \| Delta | Count of seconds during this interval where there was:
ATU-C:(CRC-8 summed over all bearer channels) >=18 OR
LOS >=1 OR SEF >=1 OR LPR >=1
ATU-R:(FEBE summed over all bearer channels) >=18 OR
LOS-FE >=1 OR RDI >=1 OR LPR-FE >=1 .
This parameter is inhibited during UAS. | count | s | 1 |
| <a id="interface-xdsl-line-errors-uas-delta"></a>xdsl_line_errors_uas_delta | UInt32 | Interface \| xDSL \| Line \| Errors \| UAS \| Delta | The UAS counts the seconds when the port is not in the activating status. For the port which is being activated, ATUR-UAS increases. When the port is in activating and deactivating period, the statistics of unavailable seconds do not increase. | count | s | 1 |
| <a id="interface-xdsl-line-noise-margin-downstream"></a>xdsl_line_noise_margin_down | Int16 | Interface \| xDSL \| Line \| Noise Margin \| Downstream | Noise Margin as seen by this ATU with respect to its transmitted signal in tenth dB. | dB | dB | 1 |
| <a id="interface-xdsl-line-noise-margin-upstream"></a>xdsl_line_noise_margin_up | Int16 | Interface \| xDSL \| Line \| Noise Margin \| Upstream | Noise Margin as seen by this ATU with respect to its received signal in tenth dB. | dB | dB | 1 |
| <a id="interface-xdsl-line-snr-downstream"></a>xdsl_line_snr_down | UInt16 | Interface \| xDSL \| Line \| SNR \| Downstream | (Signal-to-noise ratio) Measured difference in level of a desired signal to the level of background noise. | dB | dB | 1 |
| <a id="interface-xdsl-line-snr-upstream"></a>xdsl_line_snr_up | UInt16 | Interface \| xDSL \| Line \| SNR \| Upstream | (Signal-to-noise ratio) Measured difference in level of a desired signal to the level of background noise. | dB | dB | 1 |
| <a id="interface-xdsl-line-txpower-downstream"></a>xdsl_line_txpower_down | UInt16 | Interface \| xDSL \| Line \| TxPower \| Downstream | (≈ voltage) with which device sends its signal to the cable. | dB | dB | 1 |
| <a id="interface-xdsl-line-txpower-upstream"></a>xdsl_line_txpower_up | UInt16 | Interface \| xDSL \| Line \| TxPower \| Upstream | (≈ voltage) with which device sends its signal to the cable. | dB | dB | 1 |