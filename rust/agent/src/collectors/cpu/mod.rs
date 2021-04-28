// ---------------------------------------------------------------------
// cpu collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
mod out;
mod platform;
pub use config::CpuConfig;
pub use out::CpuOut;
pub use platform::PlatformCpuOut;

cfg_if::cfg_if! {
    if #[cfg(feature = "cpu")] {
        mod collector;
        pub use collector::CpuCollector;
    } else {
        use super::StubCollector;
        pub type CpuCollector = StubCollector<MemoryConfig>;
    }
}
