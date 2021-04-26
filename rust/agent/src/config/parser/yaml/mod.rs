// ---------------------------------------------------------------------
// YamlParser
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

cfg_if::cfg_if! {
    if #[cfg(feature = "config-yaml")] {
        mod base;
        pub use base::YamlParser;
    } else {
        use super::base::StubParser;
        pub type YamlParser = StubParser;
    }
}
