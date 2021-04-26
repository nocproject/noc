// ---------------------------------------------------------------------
// File config resolver
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

cfg_if::cfg_if! {
    if #[cfg(feature = "config-static")] {
        mod base;
        pub use base::StaticResolver;
    } else {
        use super::super::base::StubResolver;
        pub type FileResolver = StubResolver;
    }
}
