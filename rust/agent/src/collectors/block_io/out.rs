// ---------------------------------------------------------------------
// BlockIoOit
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Serialize;

#[derive(Serialize)]
pub struct BlockIoOut {
    pub read_ios: usize,
    pub read_merges: usize,
    pub read_sectors: usize,
    pub read_ticks: usize,
    pub write_ios: usize,
    pub write_merges: usize,
    pub write_sectors: usize,
    pub write_ticks: usize,
    pub in_flight: usize,
    pub io_ticks: usize,
    pub time_in_queue: usize,
}
