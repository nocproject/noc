// ---------------------------------------------------------------------
// DnsOut structure
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Serialize;

#[derive(Serialize)]
pub struct DnsOut {
    pub total: usize,
    pub success: usize,
    pub failed: usize,
    pub min: u64,
    pub max: u64,
    pub avg: u64,
    pub jitter: u64,
}
