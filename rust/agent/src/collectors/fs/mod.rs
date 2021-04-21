// ---------------------------------------------------------------------
// fs collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
pub use config::FsConfig;

cfg_if::cfg_if! {
    if #[cfg(feature = "fs")] {
        mod collector;
        pub use collector::FsCollector;
    } else {
        use super::StubCollector;
        pub type FsCollector = StubCollector<FsConfig>;
    }
}
