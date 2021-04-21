// ---------------------------------------------------------------------
// network collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
pub use config::NetworkConfig;

cfg_if::cfg_if! {
    if #[cfg(feature = "network")] {
        mod collector;
        pub use collector::NetworkCollector;
    } else {
        use super::StubCollector;
        pub type NetworkCollector = StubCollector<NetworkConfig>;
    }
}
