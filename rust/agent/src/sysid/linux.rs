// ---------------------------------------------------------------------
// Linux implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

pub use super::{SysId, SysIdBuilder, MAC};
use std::convert::TryFrom;
use std::fs;

impl SysIdBuilder for SysId {
    fn new() -> SysId {
        log::debug!("Using linux SysId");
        // @todo: Serial number
        let serial: Option<String> = None;
        // Get IP addresses
        let ip: Vec<String> = Self::get_ip();
        // Iterate /sys/class/net for interface macs
        let mut mac: Vec<String> = Vec::new();
        if let Ok(dir_iter) = fs::read_dir("/sys/class/net/") {
            for entry in dir_iter.flatten() {
                let if_path = entry.path();
                let mac_path = if_path.join("address");
                if let Ok(mac_data) = fs::read_to_string(mac_path) {
                    if let Ok(m) = MAC::try_from(mac_data) {
                        if !m.is_ignored() {
                            mac.push(m.to_string());
                        }
                    }
                }
            }
        }
        SysId { serial, ip, mac }
    }
}
