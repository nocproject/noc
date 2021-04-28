// ---------------------------------------------------------------------
// NetworkOut
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Serialize;

#[derive(Serialize)]
pub struct NetworkOut {
    pub ts: String,
    pub collector: &'static str,
    pub labels: Vec<String>,
    //
    pub rx_bytes: u64,
    pub tx_bytes: u64,
    pub rx_packets: u64,
    pub tx_packets: u64,
    pub rx_errors: u64,
    pub tx_errors: u64,
}
