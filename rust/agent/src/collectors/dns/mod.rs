// ---------------------------------------------------------------------
// dns collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
pub use config::DnsConfig;

cfg_if::cfg_if! {
    if #[cfg(feature = "dns")] {
        mod collector;
        pub use collector::DnsCollector;
    } else {
        use super::StubCollector;
        pub type DNSCollector = StubCollector<DNSConfig>;
    }
}
