// ---------------------------------------------------------------------
// modbus-tcp collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
mod out;
pub use config::ModbusTcpConfig;
pub use out::ModbusTcpOut;

cfg_if::cfg_if! {
    if #[cfg(feature = "modbus-tcp")] {
        mod collector;
        pub use collector::ModbusTcpCollector;
    } else {
        use super::StubCollector;
        pub type ModbusTcpCollector = StubCollector<FsConfig>;
    }
}
