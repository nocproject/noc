// ---------------------------------------------------------------------
// dns collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::DnsOut;
use crate::collectors::{Collectable, CollectorConfig, Id, Repeatable, Status};
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use crate::timing::Timing;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use std::str::FromStr;
use std::time::Instant;
use trust_dns_proto::rr::record_type::RecordType;
use trust_dns_proto::xfer::dns_request::DnsRequestOptions;
use trust_dns_resolver::TokioAsyncResolver;

const NAME: &str = "dns";

#[derive(Id, Repeatable)]
pub struct DnsCollector {
    pub id: String,
    pub interval: u64,
    pub labels: Vec<String>,
    pub query: String,
    pub query_type: String,
    pub record_type: RecordType,
    pub n: usize,
    pub min_success: usize,
}

impl TryFrom<&ZkConfigCollector> for DnsCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Dns(config) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
                labels: value.labels.clone(),
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
    async fn collect(&self) -> Result<Status, AgentError> {
        let resolver = TokioAsyncResolver::tokio_from_system_conf()
            .map_err(|e| AgentError::ConfigurationError(e.to_string()))?;
        let mut success: usize = 0;
        let mut timing = Timing::new();
        let total = self.n;
        let ts = self.get_timestamp();
        for i in 0..total {
            log::debug!(
                "[{}] {} lookup #{}: {}",
                &self.id,
                &self.query_type,
                i,
                &self.query
            );
            let t0 = Instant::now();
            match resolver
                .lookup(
                    self.query.as_ref(),
                    self.record_type,
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
        let failed = self.n - success;
        self.feed(&DnsOut {
            // Common
            ts: ts.clone(),
            collector: NAME,
            labels: self.labels.clone(),
            // Metrics
            total,
            success,
            failed,
            min_ns: timing.min_ns,
            max_ns: timing.max_ns,
            avg_ns: timing.avg_ns,
            jitter_ns: timing.jitter_ns,
        })
        .await?;
        Ok(Status::Ok)
    }
}
