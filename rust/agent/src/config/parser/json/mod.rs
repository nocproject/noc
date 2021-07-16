// ---------------------------------------------------------------------
// JsonParser
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

cfg_if::cfg_if! {
    if #[cfg(feature = "config-json")] {
        mod base;
        pub use base::JsonParser;
    } else {
        use super::base::StubParser;
        pub type JsonParser = StubParser;
    }
}
