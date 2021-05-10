// ---------------------------------------------------------------------
// TwampSenderOut
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Serialize;

#[derive(Serialize)]
pub struct TwampSenderOut {
    pub tx_packets: usize,
    pub rx_packets: usize,
    pub tx_bytes: usize,
    pub rx_bytes: usize,
    pub duration_ns: u64,
    pub tx_pps: u64,
    pub rx_pps: u64,
    pub tx_bitrate: u64,
    pub rx_bitrate: u64,
    // Inbound
    pub in_min_delay_ns: u64,
    pub in_max_delay_ns: u64,
    pub in_avg_delay_ns: u64,
    pub in_jitter_ns: u64,
    pub in_loss: usize,
    // Outbound
    pub out_min_delay_ns: u64,
    pub out_max_delay_ns: u64,
    pub out_avg_delay_ns: u64,
    pub out_jitter_ns: u64,
    pub out_loss: usize,
    // Round-trip
    pub rt_min_delay_ns: u64,
    pub rt_max_delay_ns: u64,
    pub rt_avg_delay_ns: u64,
    pub rt_jitter_ns: u64,
    pub rt_loss: usize,
}
