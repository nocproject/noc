// ---------------------------------------------------------------------
// uptime collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
pub use config::UptimeConfig;

cfg_if::cfg_if! {
    if #[cfg(feature = "uptime")] {
        mod collector;
        pub use collector::UptimeCollector;
    } else {
        use super::StubCollector;
        pub type UptimeCollector = StubCollector<UptimeConfig>;
    }
}
