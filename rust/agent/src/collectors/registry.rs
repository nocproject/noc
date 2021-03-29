// ---------------------------------------------------------------------
// Collectors registry
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::dns::{DnsCollector, DnsConfig};
use super::test::{TestCollector, TestConfig};
use super::twamp_reflector::{TwampReflectorCollector, TwampReflectorConfig};
use super::twamp_sender::{TwampSenderCollector, TwampSenderConfig};
use super::Runnable;
use crate::zk::ZkConfigCollector;
use enum_dispatch::enum_dispatch;
use serde::Deserialize;
use std::convert::TryFrom;
use std::error::Error;

/// Collector config variants.
/// Each collector must have own variant.
/// Use
/// `#[serde(rename = "<name>")]`
/// To bind particular collector with `type` field of configuration JSON
#[derive(Deserialize, Debug, Clone)]
#[serde(tag = "type")]
pub enum CollectorConfig {
    #[serde(rename = "dns")]
    Dns(DnsConfig),
    #[serde(rename = "test")]
    Test(TestConfig),
    #[serde(rename = "twamp_reflector")]
    TwampReflector(TwampReflectorConfig),
    #[serde(rename = "twamp_sender")]
    TwampSender(TwampSenderConfig),
}

/// Enumeration of collectors. Each collector must be added as separate member of enum.
/// Each collector must implement Runnable trait.
#[enum_dispatch]
pub enum Collectors {
    Dns(DnsCollector),
    Test(TestCollector),
    TwampReflector(TwampReflectorCollector),
    TwampSender(TwampSenderCollector),
}

/// Config to collector conversion.
/// Add ::try_from for every new collector.
impl TryFrom<&ZkConfigCollector> for Collectors {
    type Error = Box<dyn Error>;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        Ok(match value.config {
            CollectorConfig::Dns(_) => Collectors::Dns(DnsCollector::try_from(value)?),
            CollectorConfig::Test(_) => Collectors::Test(TestCollector::try_from(value)?),
            CollectorConfig::TwampReflector(_) => {
                Collectors::TwampReflector(TwampReflectorCollector::try_from(value)?)
            }
            CollectorConfig::TwampSender(_) => {
                Collectors::TwampSender(TwampSenderCollector::try_from(value)?)
            }
        })
    }
}
