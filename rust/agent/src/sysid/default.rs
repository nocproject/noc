// ---------------------------------------------------------------------
// Default implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

pub use super::{SysId, SysIdBuilder};

impl SysIdBuilder for SysId {
    fn new() -> SysId {
        log::debug!("Using default SysId");
        SysId {
            serial: None,
            ip: Vec::new(),
            mac: Vec::new(),
        }
    }
}
