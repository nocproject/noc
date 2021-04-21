// ---------------------------------------------------------------------
// dns collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::collectors::{Collectable, CollectorConfig, Id, Repeatable, Status};
use crate::error::AgentError;
use crate::timing::Timing;
use crate::zk::ZkConfigCollector;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use std::str::FromStr;
use std::time::Duration;
use std::time::Instant;
use trust_dns_proto::rr::record_type::RecordType;
use trust_dns_proto::xfer::dns_request::DnsRequestOptions;
use trust_dns_resolver::TokioAsyncResolver;

#[derive(Id, Repeatable)]
pub struct DnsCollector {
    pub id: String,
    pub interval: u64,
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
        log::debug!(
            "[{}] total/success/failed={}/{}/{}, min/max/avg/jitter={:?}/{:?}/{:?}/{:?}",
            &self.id,
            total,
            success,
            failed,
            Duration::from_nanos(timing.min_ns),
            Duration::from_nanos(timing.max_ns),
            Duration::from_nanos(timing.avg_ns),
            Duration::from_nanos(timing.jitter_ns),
        );
        Ok(Status::Ok)
    }
}
