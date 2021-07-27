// ---------------------------------------------------------------------
// modbus-rtu collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
mod out;
pub use config::ModbusRtuConfig;
pub use out::ModbusRtuOut;

cfg_if::cfg_if! {
    if #[cfg(feature = "modbus-rtu")] {
        mod collector;
        pub use collector::ModbusRtuCollector;
    } else {
        use super::StubCollector;
        pub type ModbusRtuCollector = StubCollector<FsConfig>;
    }
}
