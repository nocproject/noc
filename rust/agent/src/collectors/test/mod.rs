// ---------------------------------------------------------------------
// test collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
mod out;
pub use config::TestConfig;
pub use out::TestOut;

cfg_if::cfg_if! {
    if #[cfg(feature = "test")] {
        mod collector;
        pub use collector::TestCollector;
    } else {
        use super::StubCollector;
        pub type TestCollector = StubCollector<TestConfig>;
    }
}
