// ---------------------------------------------------------------------
// ZeroConf config resolver
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Resolver;
use crate::cli::CliArgs;
use crate::config::reader::ConfigReader;
use crate::config::ZkConfig;
use crate::error::AgentError;
use crate::state::AgentState;
use crate::sysid::{SysId, SysIdBuilder};
use async_trait::async_trait;
use std::convert::TryFrom;
use std::str;
use tokio::time::{sleep, Duration};
use trust_dns_resolver::TokioAsyncResolver;

const DEFAULT_CONFIG_RETRY_INTERVAL: u64 = 10;

pub struct ZkResolver {
    pub state_path: Option<String>,
    pub config_interval: u64,
    pub disable_cert_validation: bool,
    pub state: AgentState,
    pub sys_id: SysId,
}

impl TryFrom<CliArgs> for ZkResolver {
    type Error = AgentError;

    fn try_from(args: CliArgs) -> Result<ZkResolver, Self::Error> {
        match (&args.bootstrap_state, &args.zk_url) {
            (None, None) => Err(AgentError::ConfigurationError(
                "--bootstrap-state or --zk-url options are required".to_string(),
            )),
            _ => {
                let mut state = AgentState::from_file_or_default(args.bootstrap_state.clone());
                if let Some(zk_url) = args.zk_url {
                    state.set_zeroconf_url(zk_url);
                }
                Ok(ZkResolver {
                    state_path: args.bootstrap_state.clone(),
                    config_interval: DEFAULT_CONFIG_RETRY_INTERVAL,
                    disable_cert_validation: args.disable_cert_validation,
                    sys_id: SysId::new(),
                    state,
                })
            }
        }
    }
}

#[async_trait]
impl Resolver for ZkResolver {
    fn is_failable(&self) -> bool {
        true
    }
    fn is_repeatable(&self) -> bool {
        true
    }
    async fn bootstrap(&mut self) -> Result<(), AgentError> {
        if self.state.has_url() {
            // Already set
            return Ok(());
        }
        //
        let url = self.get_from_dns().await?;
        log::info!("Resolved zeroconf url to {}", url);
        self.state.set_zeroconf_url(url);
        self.state.try_save(self.state_path.clone());
        Ok(())
    }
    fn get_reader(&self) -> Result<ConfigReader, AgentError> {
        match &self.state.zeroconf_url {
            Some(url) => ConfigReader::from_url(
                url.into(),
                Some(&self.sys_id),
                Some(&self.state),
                !self.disable_cert_validation,
            )
            .ok_or_else(|| AgentError::ConfigurationError("Invalid schema".to_string())),
            None => Err(AgentError::ConfigurationError(
                "Zeroconf url is not resolved".to_string(),
            )),
        }
    }
    // Apply collected config
    fn apply(&mut self, config: &ZkConfig) -> Result<(), AgentError> {
        let zk_interval = config.config.zeroconf.interval;
        if zk_interval > 0 && zk_interval != self.config_interval {
            log::info!(
                "Changing config refresh interval: {} -> {}",
                self.config_interval,
                zk_interval
            );
            self.config_interval = zk_interval;
        }
        if let Some(agent_id) = config.config.zeroconf.id {
            self.state.set_agent_id(agent_id);
        }
        if let Some(agent_key) = config.config.zeroconf.key.clone() {
            self.state.set_agent_key(agent_key);
        }
        self.state.try_save(self.state_path.clone());
        Ok(())
    }
    // Wait for next round
    async fn sleep(&self, _status: bool) {
        sleep(Duration::from_secs(self.config_interval)).await;
    }
}

impl ZkResolver {
    async fn get_from_dns(&mut self) -> Result<String, AgentError> {
        log::debug!("Resolving zeroconf URL via DNS");
        let resolver = TokioAsyncResolver::tokio_from_system_conf()
            .map_err(|e| AgentError::ConfigurationError(e.to_string()))?;
        loop {
            // List of RR to check
            let queries = vec!["_noc-zeroconf.", "_noc-zeroconf.getnoc.com."];
            // Send queries
            for q in queries {
                log::debug!("Resolving {}", q);
                match resolver.txt_lookup(q).await {
                    Ok(response) => {
                        log::debug!("Response: {:?}", response);
                        for r in response.iter() {
                            for resp in r.txt_data() {
                                match str::from_utf8(resp) {
                                    Ok(x) => return Ok(x.into()),
                                    Err(e) => log::debug!("Failed to decode response: {}", e),
                                }
                            }
                        }
                    }
                    Err(e) => log::debug!("Cannot resolve {}: {}", q, e),
                }
            }
            log::debug!("Cannot resolve zeroconf url. Waiting.");
            sleep(Duration::from_secs(3)).await;
        }
    }
}
