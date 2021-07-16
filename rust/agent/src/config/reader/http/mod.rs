// ---------------------------------------------------------------------
// HttpReaedr module
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

cfg_if::cfg_if! {
    if #[cfg(feature = "config-http")] {
        mod base;
        pub use base::HttpReader;
    } else {
        use super::base::StubReader;
        pub type HttpReader = StubReader;
    }
}
