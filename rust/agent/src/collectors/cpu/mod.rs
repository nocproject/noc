// ---------------------------------------------------------------------
// cpu collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
pub use config::CpuConfig;

cfg_if::cfg_if! {
    if #[cfg(feature = "cpu")] {
        mod out;
        mod platform;
        pub use out::CpuOut;
        pub use platform::PlatformCpuOut;
        mod collector;
        pub use collector::CpuCollector;
    } else {
        use super::StubCollector;
        pub type CpuCollector = StubCollector<CpuConfig>;
    }
}
