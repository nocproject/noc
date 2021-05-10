// ---------------------------------------------------------------------
// fs collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, Collector, NoConfig, Schedule, Status};
use super::FsOut;
use crate::error::AgentError;
use async_trait::async_trait;
use systemstat::{Platform, System};

pub struct ConfigStub;
pub type FsCollector = Collector<NoConfig<ConfigStub>>;

#[async_trait]
impl Collectable for FsCollector {
    const NAME: &'static str = "fs";
    type Output = FsOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = Self::get_timestamp();
        let mounts = sys
            .mounts()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        for fs in mounts.iter() {
            if !FsCollector::is_ignored_fs_type(&fs.fs_type, &fs.fs_mounted_on) {
                let mut labels = self.get_labels();
                labels.push(format!("noc::fs::{}", fs.fs_mounted_on));
                labels.push(format!("noc::fstype::{}", fs.fs_type));
                self.feed(
                    ts.clone(),
                    labels,
                    &FsOut {
                        files: fs.files,
                        files_total: fs.files_total,
                        files_avail: fs.files_avail,
                        free: fs.free.as_u64(),
                        avail: fs.avail.as_u64(),
                        total: fs.total.as_u64(),
                    },
                )
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
