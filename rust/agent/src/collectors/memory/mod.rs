// ---------------------------------------------------------------------
// memory collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
pub use config::MemoryConfig;

cfg_if::cfg_if! {
    if #[cfg(feature = "memory")] {
        mod collector;
        pub use collector::MemoryCollector;
    } else {
        use super::StubCollector;
        pub type MemoryCollector = StubCollector<MemoryConfig>;
    }
}
