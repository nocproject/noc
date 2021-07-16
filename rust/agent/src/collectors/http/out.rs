// ---------------------------------------------------------------------
// HttpOut
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Serialize;

#[derive(Serialize)]
pub struct HttpOut {
    pub time: usize,
    pub bytes: usize,
    pub compressed_bytes: u64,
}
