// ---------------------------------------------------------------------
// dns collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::DnsOut;
use crate::collectors::{Collectable, Collector, CollectorConfig, Schedule, Status};
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use crate::timing::Timing;
use async_trait::async_trait;
use std::convert::TryFrom;
use std::str::FromStr;
use std::time::Instant;
use trust_dns_proto::rr::record_type::RecordType;
use trust_dns_proto::xfer::dns_request::DnsRequestOptions;
use trust_dns_resolver::TokioAsyncResolver;

pub struct DnsCollectorConfig {
    pub query: String,
    pub query_type: String,
    pub record_type: RecordType,
    pub n: usize,
    pub min_success: usize,
}

pub type DnsCollector = Collector<DnsCollectorConfig>;

impl TryFrom<&ZkConfigCollector> for DnsCollectorConfig {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Dns(config) => Ok(Self {
                query: config.query.clone(),
                query_type: config.query_type.clone(),
                record_type: RecordType::from_str(&config.query_type)
                    .map_err(|_| AgentError::ConfigurationError("Invalid record type".into()))?,
                n: config.n,
                min_success: config.min_success,
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for DnsCollector {
    const NAME: &'static str = "dns";
    type Output = DnsOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let resolver = TokioAsyncResolver::tokio_from_system_conf()
            .map_err(|e| AgentError::ConfigurationError(e.to_string()))?;
        let mut success: usize = 0;
        let mut timing = Timing::new();
        let total = self.data.n;
        let ts = Self::get_timestamp();
        for i in 0..total {
            log::debug!(
                "[{}] {} lookup #{}: {}",
                &self.id,
                &self.data.query_type,
                i,
                &self.data.query
            );
            let t0 = Instant::now();
            match resolver
                .lookup(
                    self.data.query.as_ref(),
                    self.data.record_type,
                    DnsRequestOptions::default(),
                )
                .await
            {
                Ok(_) => {
                    success += 1;
                }
                Err(e) => {
                    log::debug!("[{}] Failed to resolve: {}", &self.id, e);
                }
            }
            timing.register(t0.elapsed().as_nanos() as u64);
        }
        timing.done();
        let failed = self.data.n - success;
        self.feed(
            ts.clone(),
            self.get_labels(),
            &DnsOut {
                // Common
                // Metrics
                total,
                success,
                failed,
                min_ns: timing.min_ns,
                max_ns: timing.max_ns,
                avg_ns: timing.avg_ns,
                jitter_ns: timing.jitter_ns,
            },
        )
        .await?;
        Ok(Status::Ok)
    }
}
