// ---------------------------------------------------------------------
// DNS collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::collectors::base::{Collectable, Collector, Status};
use crate::timing::Timing;
use crate::zk::Configurable;
use async_trait::async_trait;
use serde::Deserialize;
use std::error::Error;
use std::str::FromStr;
use std::time::Duration;
use std::time::Instant;
use trust_dns_proto::rr::record_type::RecordType;
use trust_dns_proto::xfer::dns_request::DnsRequestOptions;
use trust_dns_resolver::TokioAsyncResolver;

#[derive(Deserialize, Debug)]
pub struct DNSConfig {
    query: String,
    #[serde(default = "default_type_a")]
    query_type: String,
    #[serde(default = "default_one")]
    n: usize,
    #[serde(default = "default_one")]
    min_success: usize,
}

impl Configurable<DNSConfig> for DNSConfig {}

pub type DNSCollector = Collector<DNSConfig>;

#[async_trait]
impl Collectable for DNSCollector {
    async fn collect(&self) -> Result<Status, Box<dyn Error>> {
        let resolver = TokioAsyncResolver::tokio_from_system_conf()?;
        let record_type = RecordType::from_str(self.config.query_type.as_ref())?;
        let mut success: usize = 0;
        let mut timing = Timing::new();
        let total = self.config.n;
        for i in 0..total {
            log::debug!(
                "[{}] {} lookup #{}: {}",
                &self.id,
                &self.config.query_type,
                i,
                &self.config.query
            );
            let t0 = Instant::now();
            match resolver
                .lookup(
                    self.config.query.as_ref(),
                    record_type,
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
        let failed = self.config.n - success;
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

fn default_type_a() -> String {
    "A".into()
}

fn default_one() -> usize {
    1
}
