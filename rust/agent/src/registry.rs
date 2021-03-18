// ---------------------------------------------------------------------
// Collector's registry
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::collectors::base::Runnable;
#[cfg(feature = "dns")]
use crate::collectors::dns::DNSCollector;
#[cfg(feature = "test")]
use crate::collectors::test::TestCollector;
#[cfg(feature = "twamp-reflector")]
use crate::collectors::twamp_reflector::TWAMPReflectorCollector;
#[cfg(feature = "twamp-sender")]
use crate::collectors::twamp_sender::TWAMPSenderCollector;
use crate::zk::ZkConfigCollector;
use std::error::Error;

pub fn get_collector(
    config: &ZkConfigCollector,
) -> Result<Box<dyn Runnable + Send + Sync>, Box<dyn Error>> {
    match config.collector_type.as_str() {
        #[cfg(feature = "dns")]
        "dns" => Ok(Box::new(DNSCollector::new_from(config)?)),
        #[cfg(feature = "test")]
        "test" => Ok(Box::new(TestCollector::new_from(config)?)),
        #[cfg(feature = "twamp-reflector")]
        "twamp_reflector" => Ok(Box::new(TWAMPReflectorCollector::new_from(config)?)),
        #[cfg(feature = "twamp-sender")]
        "twamp_sender" => Ok(Box::new(TWAMPSenderCollector::new_from(config)?)),
        _ => Err(format!("Unknown collector: {}", config.collector_type).into()),
    }
}
