// ---------------------------------------------------------------------
// block-io collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
mod out;
pub use config::BlockIoConfig;
pub use out::BlockIoOut;

cfg_if::cfg_if! {
    if #[cfg(feature = "block-io")] {
        mod collector;
        pub use collector::BlockIoCollector;
    } else {
        use super::StubCollector;
        pub type BlockIoCollector = StubCollector<BlockIoConfig>;
    }
}
