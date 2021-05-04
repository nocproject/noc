// ---------------------------------------------------------------------
// Features compatibility check
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

#[allow(unused_imports)]
use std::compile_error;

// Features are organized into 4 groups. At least one feature in every group must be activated

// Config discovery
#[cfg(not(any(feature = "config-static", feature = "config-zk")))]
compile_error!("At least one config discovery feature must be activated.");

// Config reader
#[cfg(not(any(feature = "config-file")))]
compile_error!("At least one config reader feature must be activated.");

// Config format
#[cfg(not(any(feature = "config-json", feature = "config-yaml")))]
compile_error!("At least one config format feature must be activated.");

// Collectors
#[cfg(not(any(
    feature = "block-io",
    feature = "cpu",
    feature = "dns",
    feature = "fs",
    feature = "memory",
    feature = "network",
    feature = "test",
    feature = "twamp-reflector",
    feature = "twamp-sender",
    feature = "uptime"
)))]
compile_error!("At least one collector feature must be activated.");
