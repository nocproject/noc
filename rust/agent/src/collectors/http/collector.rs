// ---------------------------------------------------------------------
// http collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::{Collectable, Collector, CollectorConfig, Status};
use super::HttpOut;
use crate::collectors::Schedule;
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use async_trait::async_trait;
use std::convert::TryFrom;
use std::time::Instant;

pub struct HttpCollectorConfig {
    pub url: String,
}

pub type HttpCollector = Collector<HttpCollectorConfig>;

impl TryFrom<&ZkConfigCollector> for HttpCollectorConfig {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Http(config) => Ok(Self {
                url: config.url.clone(),
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for HttpCollector {
    const NAME: &'static str = "http";
    type Output = HttpOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let ts = Self::get_timestamp();
        let start = Instant::now();
        let client = reqwest::Client::builder()
            .gzip(true)
            .build()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        let mut resp = client
            .get(&self.data.url)
            .send()
            .await
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        let time = start.elapsed().as_nanos() as usize;
        let mut bytes = 0;
        while let Some(chunk) = resp
            .chunk()
            .await
            .map_err(|e| AgentError::InternalError(e.to_string()))?
        {
            bytes += chunk.len();
        }
        let compressed_bytes = match &resp.content_length() {
            Some(x) => *x,
            None => bytes as u64,
        };
        self.feed(
            ts.clone(),
            self.get_labels(),
            &HttpOut {
                time,
                bytes,
                compressed_bytes,
            },
        )
        .await?;
        Ok(Status::Ok)
    }
}
