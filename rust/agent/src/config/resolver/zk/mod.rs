// ---------------------------------------------------------------------
// ZeroConf config resolver
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

cfg_if::cfg_if! {
    if #[cfg(feature = "config-zk")] {
        mod base;
        pub use base::ZkResolver;
    } else {
        use super::base::StubResolver;
        pub type ZkResolver = StubResolver;
    }
}
