// ---------------------------------------------------------------------
// network collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
mod out;
pub use config::NetworkConfig;
pub use out::NetworkOut;

cfg_if::cfg_if! {
    if #[cfg(feature = "network")] {
        mod collector;
        pub use collector::NetworkCollector;
    } else {
        use super::StubCollector;
        pub type NetworkCollector = StubCollector<NetworkConfig>;
    }
}
