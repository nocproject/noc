// ---------------------------------------------------------------------
// MemoryOut struct
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::PlatformMemoryOut;
use serde::Serialize;

#[derive(Serialize)]
pub struct MemoryOut {
    pub ts: String,
    pub collector: &'static str,
    pub labels: Vec<String>,
    //
    pub total: u64,
    pub free: u64,
    //
    #[serde(flatten)]
    pub platform: PlatformMemoryOut,
}
