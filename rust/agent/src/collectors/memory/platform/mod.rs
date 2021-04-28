// ---------------------------------------------------------------------
// Platform-specific memory information
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

cfg_if::cfg_if! {
    if #[cfg(target_os = "linux")] {
        pub mod linux;
        pub use linux::PlatformMemoryOut;
    } else if #[cfg(target_os = "windows")] {
        pub mod windows;
        pub use windows::PlatformMemoryOut;
    } else if #[cfg(target_os = "freebsd")] {
        pub mod freebsd;
        pub use freebsd::PlatformMemoryOut;
    } else if #[cfg(target_os = "openbsd")] {
        pub mod openbsd;
        pub use openbsd::PlatformMemoryOut;
    } else if #[cfg(target_os = "macos")] {
        pub mod macos;
        pub use macos::PlatformMemoryOut;
    } else {
        pub mod default;
        pub use default::PlatformMemoryOut;
    }
}
