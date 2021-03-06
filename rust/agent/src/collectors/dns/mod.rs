// ---------------------------------------------------------------------
// dns collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
mod out;
pub use config::DnsConfig;
pub use out::DnsOut;

cfg_if::cfg_if! {
    if #[cfg(feature = "dns")] {
        mod collector;
        pub use collector::DnsCollector;
    } else {
        use super::StubCollector;
        pub type DnsCollector = StubCollector<DnsConfig>;
    }
}
