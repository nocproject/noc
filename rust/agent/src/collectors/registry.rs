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

#[derive(Deserialize, Debug, Clone)]
#[serde(tag = "type")]
pub enum CollectorConfig {
    #[serde(rename = "dns")]
    DNSCollector(DNSConfig),
    #[serde(rename = "test")]
    TestCollector(TestConfig),
    #[serde(rename = "twamp_reflector")]
    TWAMPReflectorCollector(TWAMPReflectorConfig),
    #[serde(rename = "twamp_sender")]
    TWAMPSenderCollector(TWAMPSenderConfig),
}

#[enum_dispatch]
pub enum Collectors {
    DNSCollector(DNSCollector),
    TestCollector(TestCollector),
    TWAMPReflectorCollector(TWAMPReflectorCollector),
    TWAMPSenderCollector(TWAMPSenderCollector),
}

impl TryFrom<&ZkConfigCollector> for Collectors {
    type Error = Box<dyn Error>;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        Ok(match value.config.clone() {
            CollectorConfig::DNSCollector(c) => {
                Collectors::DNSCollector(DNSCollector::new_from(value, c)?)
            }
            CollectorConfig::TestCollector(c) => {
                Collectors::TestCollector(TestCollector::new_from(value, c)?)
            }
            CollectorConfig::TWAMPReflectorCollector(c) => {
                Collectors::TWAMPReflectorCollector(TWAMPReflectorCollector::new_from(value, c)?)
            }
            CollectorConfig::TWAMPSenderCollector(c) => {
                Collectors::TWAMPSenderCollector(TWAMPSenderCollector::new_from(value, c)?)
            }
        })
    }
}
