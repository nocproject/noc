// ---------------------------------------------------------------------
// System identification
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

pub mod util;
use std::net::Ipv4Addr;
use systemstat::{IpAddr, Platform, System};
pub use util::MAC;

#[derive(Debug)]
pub struct SysId {
    // Board serial number
    pub serial: Option<String>,
    // Network interfaces' IP addresses
    pub ip: Vec<String>,
    // Network interfaces' MAC addresses
    pub mac: Vec<String>,
}

pub trait SysIdBuilder {
    fn new() -> Self;
    fn get_ip() -> Vec<String> {
        let system = System::new();
        let mut ip = Vec::<String>::new();
        if let Ok(if_map) = system.networks() {
            for iface in if_map.values() {
                for if_addr in &iface.addrs {
                    if let IpAddr::V4(addr) = if_addr.addr {
                        if Self::is_valid_ipv4(addr) {
                            ip.push(format!("{:?}", addr));
                        }
                    }
                }
            }
        }
        ip
    }
    fn is_valid_ipv4(addr: Ipv4Addr) -> bool {
        !addr.is_loopback() && !addr.is_multicast()
    }
}

// Install implementation of SysIdBuilder
cfg_if::cfg_if! {
    if #[cfg(target_os = "linux")] {
        pub mod linux;
    } else {
        pub mod default;
    }
}
