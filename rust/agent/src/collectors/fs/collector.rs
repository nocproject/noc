// ---------------------------------------------------------------------
// fs collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use super::FsOut;
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};

const NAME: &str = "fs";

#[derive(Id, Repeatable)]
pub struct FsCollector {
    pub id: String,
    pub service: String,
    pub interval: u64,
    pub labels: Vec<String>,
}

impl TryFrom<&ZkConfigCollector> for FsCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Fs(_) => Ok(Self {
                id: value.get_id(),
                service: value.get_service(),
                interval: value.get_interval(),
                labels: value.get_labels(),
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for FsCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = self.get_timestamp();
        let mounts = sys
            .mounts()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        for fs in mounts.iter() {
            if !FsCollector::is_ignored_fs_type(&fs.fs_type, &fs.fs_mounted_on) {
                let mut labels = self.labels.clone();
                labels.push(format!("noc::fs::{}", fs.fs_mounted_on));
                labels.push(format!("noc::fstype::{}", fs.fs_type));
                self.feed(&FsOut {
                    ts: ts.clone(),
                    service: self.service.clone(),
                    collector: NAME,
                    labels,
                    //
                    files: fs.files,
                    files_total: fs.files_total,
                    files_avail: fs.files_avail,
                    free: fs.free.as_u64(),
                    avail: fs.avail.as_u64(),
                    total: fs.total.as_u64(),
                })
                .await?;
            }
        }
        Ok(Status::Ok)
    }
}

impl FsCollector {
    // Filter out internal filesystems
    #[cfg(target_os = "linux")]
    fn is_ignored_fs_type(fs_type: &str, fs_mounted_on: &str) -> bool {
        // Ignore by type
        if matches!(fs_type, "proc" | "devpts" | "sysfs" | "cgroup" | "overlay") {
            return true;
        }
        // Ignore by prefix
        fs_mounted_on.starts_with("/proc/")
            || fs_mounted_on.starts_with("/dev/")
            || fs_mounted_on.starts_with("/sys/")
    }
    #[cfg(not(target_os = "linux"))]
    fn is_ignored_fs_type(fs_type: &str, fs_mounted_on: &str) -> bool {
        false
    }
}
