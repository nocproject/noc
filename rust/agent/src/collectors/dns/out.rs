// ---------------------------------------------------------------------
// DnsOut structure
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Serialize;

#[derive(Serialize)]
pub struct DnsOut {
    pub ts: String,
    pub collector: &'static str,
    pub labels: Vec<String>,
    //
    pub total: usize,
    pub success: usize,
    pub failed: usize,
    pub min_ns: u64,
    pub max_ns: u64,
    pub avg_ns: u64,
    pub jitter_ns: u64,
}
