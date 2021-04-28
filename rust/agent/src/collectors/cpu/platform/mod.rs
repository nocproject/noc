// ---------------------------------------------------------------------
// Platform-dependent CPU information
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

cfg_if::cfg_if! {
    if #[cfg(target_os = "linux")] {
        pub mod linux;
        pub use linux::PlatformCpuOut;
    } else {
        pub mod default;
        pub use default:PlatformCpuOut;
    }
}
