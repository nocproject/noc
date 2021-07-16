// ---------------------------------------------------------------------
// http collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
mod out;
pub use config::HttpConfig;
pub use out::HttpOut;

cfg_if::cfg_if! {
    if #[cfg(feature = "http")] {
        mod collector;
        pub use collector::HttpCollector;
    } else {
        use super::StubCollector;
        pub type HttpCollector = StubCollector<HttpConfig>;
    }
}
