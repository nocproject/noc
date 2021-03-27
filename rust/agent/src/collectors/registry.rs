// ---------------------------------------------------------------------
// Collectors registry
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::dns::{DNSCollector, DNSConfig};
use super::test::{TestCollector, TestConfig};
use super::twamp_reflector::{TWAMPReflectorCollector, TWAMPReflectorConfig};
use super::twamp_sender::{TWAMPSenderCollector, TWAMPSenderConfig};
use super::Runnable;
use crate::zk::ZkConfigCollector;
use enum_dispatch::enum_dispatch;
use serde::Deserialize;
use std::convert::TryFrom;
use std::error::Error;

/// Collector config variants.
/// Each collector must have own variant.
/// Use
/// #[serde(rename = "<name>")]
/// To bind particular collector with `type` field of configuration JSON
#[derive(Deserialize, Debug, Clone)]
#[serde(tag = "type")]
pub enum CollectorConfig {
    #[serde(rename = "dns")]
    DNS(DNSConfig),
    #[serde(rename = "test")]
    Test(TestConfig),
    #[serde(rename = "twamp_reflector")]
    TWAMPReflector(TWAMPReflectorConfig),
    #[serde(rename = "twamp_sender")]
    TWAMPSender(TWAMPSenderConfig),
}

/// Enumeration of collectors. Each collector must be added as separate member of enum.
/// Each collector must implement Runnable trait.
#[enum_dispatch]
pub enum Collectors {
    DNS(DNSCollector),
    Test(TestCollector),
    TWAMPReflector(TWAMPReflectorCollector),
    TWAMPSender(TWAMPSenderCollector),
}

/// Config to collector conversion.
/// Add ::try_from for every new collector.
impl TryFrom<&ZkConfigCollector> for Collectors {
    type Error = Box<dyn Error>;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        Ok(match value.config {
            CollectorConfig::DNS(_) => Collectors::DNS(DNSCollector::try_from(value)?),
            CollectorConfig::Test(_) => Collectors::Test(TestCollector::try_from(value)?),
            CollectorConfig::TWAMPReflector(_) => {
                Collectors::TWAMPReflector(TWAMPReflectorCollector::try_from(value)?)
            }
            CollectorConfig::TWAMPSender(_) => {
                Collectors::TWAMPSender(TWAMPSenderCollector::try_from(value)?)
            }
        })
    }
}
