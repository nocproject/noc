// ---------------------------------------------------------------------
// Collectors registry
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::cpu::{CpuCollector, CpuConfig};
use super::dns::{DnsCollector, DnsConfig};
use super::fs::{FsCollector, FsConfig};
use super::memory::{MemoryCollector, MemoryConfig};
use super::network::{NetworkCollector, NetworkConfig};
use super::test::{TestCollector, TestConfig};
use super::twamp_reflector::{TwampReflectorCollector, TwampReflectorConfig};
use super::twamp_sender::{TwampSenderCollector, TwampSenderConfig};
use super::uptime::{UptimeCollector, UptimeConfig};
use super::Runnable;
use crate::error::AgentError;
use crate::zk::ZkConfigCollector;
use enum_dispatch::enum_dispatch;
use serde::Deserialize;
use std::convert::TryFrom;

/// Collector config variants.
/// Each collector must have own variant.
/// Use
/// `#[serde(rename = "<name>")]`
/// To bind particular collector with `type` field of configuration JSON
#[derive(Deserialize, Debug, Clone)]
#[serde(tag = "type")]
pub enum CollectorConfig {
    #[serde(rename = "cpu")]
    Cpu(CpuConfig),
    #[serde(rename = "dns")]
    Dns(DnsConfig),
    #[serde(rename = "fs")]
    Fs(FsConfig),
    #[serde(rename = "memory")]
    Memory(MemoryConfig),
    #[serde(rename = "network")]
    Network(NetworkConfig),
    #[serde(rename = "test")]
    Test(TestConfig),
    #[serde(rename = "twamp_reflector")]
    TwampReflector(TwampReflectorConfig),
    #[serde(rename = "twamp_sender")]
    TwampSender(TwampSenderConfig),
    #[serde(rename = "uptime")]
    Uptime(UptimeConfig),
}

/// Enumeration of collectors. Each collector must be added as separate member of enum.
/// Each collector must implement Runnable trait.
#[enum_dispatch]
pub enum Collectors {
    Cpu(CpuCollector),
    Dns(DnsCollector),
    Fs(FsCollector),
    Memory(MemoryCollector),
    Network(NetworkCollector),
    Test(TestCollector),
    TwampReflector(TwampReflectorCollector),
    TwampSender(TwampSenderCollector),
    Uptime(UptimeCollector),
}

/// Config to collector conversion.
/// Add ::try_from for every new collector.
impl TryFrom<&ZkConfigCollector> for Collectors {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        Ok(match value.config {
            CollectorConfig::Cpu(_) => Collectors::Cpu(CpuCollector::try_from(value)?),
            CollectorConfig::Dns(_) => Collectors::Dns(DnsCollector::try_from(value)?),
            CollectorConfig::Fs(_) => Collectors::Fs(FsCollector::try_from(value)?),
            CollectorConfig::Memory(_) => Collectors::Memory(MemoryCollector::try_from(value)?),
            CollectorConfig::Network(_) => Collectors::Network(NetworkCollector::try_from(value)?),
            CollectorConfig::Test(_) => Collectors::Test(TestCollector::try_from(value)?),
            CollectorConfig::TwampReflector(_) => {
                Collectors::TwampReflector(TwampReflectorCollector::try_from(value)?)
            }
            CollectorConfig::TwampSender(_) => {
                Collectors::TwampSender(TwampSenderCollector::try_from(value)?)
            }
            CollectorConfig::Uptime(_) => Collectors::Uptime(UptimeCollector::try_from(value)?),
        })
    }
}
