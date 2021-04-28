// ---------------------------------------------------------------------
// UptimeOut structure
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct UptimeOut {
    pub ts: String,
    pub collector: &'static str,
    pub labels: Vec<String>,
    pub uptime: u64,
}
