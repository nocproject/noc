// ---------------------------------------------------------------------
// FsOut type
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Serialize;

#[derive(Serialize)]
pub struct FsOut {
    pub ts: String,
    pub collector: &'static str,
    pub labels: Vec<String>,
    //
    pub files: usize,
    pub files_total: usize,
    pub files_avail: usize,
    pub free: u64,
    pub avail: u64,
    pub total: u64,
}
