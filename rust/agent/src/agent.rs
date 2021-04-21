/* ---------------------------------------------------------------------
 * Agent
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2021 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::cmd::CmdArgs;
use crate::collectors::{Collectors, Runnable};
use crate::error::AgentError;
use crate::nvram::Nvram;
use crate::zk::{ZkConfig, ZkConfigCollector};
use std::collections::HashMap;
use std::convert::TryFrom;
use std::fs;
use std::str;
use std::sync::Arc;
use tokio::runtime::Runtime;
use tokio::time::{interval, sleep, Duration, Interval};
use trust_dns_resolver::TokioAsyncResolver;

pub struct Agent {
    nvram: Nvram,
    zeroconf_url: Option<String>,
    resolver: Option<TokioAsyncResolver>,
    config_interval: u64,
    collectors: HashMap<String, Arc<Collectors>>,
}

const CLEAN_CONFIG_FETCH_INTERVAL: u64 = 10;
const CONFIG_RETRY_INTERVAL: u64 = 10;

impl Agent {
    pub fn new_from(_args: CmdArgs) -> Self {
        Self {
            nvram: Nvram::new(),
            zeroconf_url: None,
            resolver: None,
            config_interval: CLEAN_CONFIG_FETCH_INTERVAL,
            collectors: HashMap::new(),
        }
    }
    pub fn run(&mut self) -> Result<(), AgentError> {
        log::info!("Running agent");
        if let Err(e) = self.nvram.load() {
            log::info!("Cannot read NVRAM: {}", e);
            log::info!("Starting from clean NVRAM");
        }
        let runtime = Runtime::new()?;
        runtime.block_on(async move { self.agent_loop().await })?;
        log::info!("Stopping agent");
        Ok(())
    }
    async fn agent_loop(&mut self) -> Result<(), AgentError> {
        // Initialize resolver
        log::debug!("Initializing resolver");
        self.resolver = Some(
            TokioAsyncResolver::tokio_from_system_conf()
                .map_err(|e| AgentError::ConfigurationError(e.to_string()))?,
        );
        // Resolve zeroconf url
        if self.zeroconf_url.is_none() {
            if let Err(e) = self.resolve_zeroconf_url().await {
                log::error!("Failed to get zeroconf url: {:?}", e);
                return Err(e);
            }
        };
        log::info!(
            "Using zeroconf url: {}",
            self.zeroconf_url.as_ref().unwrap()
        );
        // Poll config and spawn tasks
        let mut config_interval = self.get_config_interval();
        loop {
            let prev_config_interval = self.config_interval;
            config_interval.tick().await;
            if let Err(e) = self.process_config().await {
                log::info!("Cannot fetch config: {:?}", e);
                sleep(Duration::from_secs(CONFIG_RETRY_INTERVAL)).await;
            }
            if self.config_interval != prev_config_interval {
                log::debug!(
                    "Changing config polling interval: {} -> {}",
                    prev_config_interval,
                    self.config_interval
                );
                config_interval = self.get_config_interval();
            }
        }
    }
    fn get_config_interval(&self) -> Interval {
        interval(Duration::from_secs(self.config_interval))
    }
    fn set_zeroconf_url(&mut self, url: &str) -> Result<(), AgentError> {
        match &self.zeroconf_url {
            Some(x) => {
                if x == url {
                    Ok(())
                } else {
                    self.zeroconf_url = Some(url.to_string());
                    self.nvram.set_zeroconf_url(url)
                }
            }
            None => {
                self.zeroconf_url = Some(url.to_string());
                self.nvram.set_zeroconf_url(url)
            }
        }
    }
    async fn resolve_zeroconf_url(&mut self) -> Result<(), AgentError> {
        // Check if agent is initialized
        if self.zeroconf_url.is_some() {
            return Ok(());
        }
        // Agent has been configured
        if self.nvram.zeroconf_url.is_some() {
            log::debug!("Using zeroconf url from NVRAM");
            return self.set_zeroconf_url(&self.nvram.zeroconf_url.as_ref().unwrap().clone());
        }
        // Agent has default configuration
        if self.nvram.default_zeroconf_url.is_some() {
            log::debug!("Using default zeroconf url from NVRAM");
            return self
                .set_zeroconf_url(&self.nvram.default_zeroconf_url.as_ref().unwrap().clone());
        }
        // Fallback to DNS
        match self.get_dns_zeroconf_url().await {
            Ok(x) => {
                log::debug!("Using zeroconf url from DNS: {}", &x);
                self.set_zeroconf_url(&x)
            }
            Err(e) => Err(AgentError::BootstrapError(e.to_string())),
        }
    }
    async fn get_dns_zeroconf_url(&self) -> Result<String, AgentError> {
        log::debug!("Resolving zeroconf URL via DNS");
        let queries = vec!["_noc-zeroconf.", "_noc-zeroconf.getnoc.com."];
        for q in queries {
            log::debug!("Resolving {}", q);
            match self.dns_query_txt(q.into()).await {
                Ok(x) => {
                    log::debug!("{} has been resolved to: {}", q, x);
                    return Ok(x);
                }
                Err(e) => {
                    log::debug!("{} cannot be resolved: {:?}", q, e);
                }
            };
        }
        Err(AgentError::NetworkError("Failed to resolve".into()))
    }
    async fn dns_query_txt(&self, query: String) -> Result<String, AgentError> {
        let response = self
            .resolver
            .as_ref()
            .unwrap()
            .txt_lookup(query)
            .await
            .map_err(|e| AgentError::NetworkError(e.to_string()))?;
        for r in response.iter() {
            log::debug!("Response: {:?}", r);
            for resp in r.txt_data() {
                match str::from_utf8(resp) {
                    Ok(x) => return Ok(x.into()),
                    Err(e) => log::debug!("Failed to decode response: {}", e),
                }
            }
        }
        Err(AgentError::NotImplementedError)
    }
    async fn process_config(&mut self) -> Result<(), AgentError> {
        let cfg = self
            .fetch_config(&self.zeroconf_url.as_ref().unwrap())
            .await?;
        // config section
        if cfg.config.zeroconf.interval != self.config_interval {
            self.config_interval = cfg.config.zeroconf.interval;
        }
        //
        for collector_cfg in cfg.collectors.iter() {
            let collector_id: String = String::from(&collector_cfg.id);
            if collector_cfg.disabled {
                log::debug!("[{}] Collector is disabled", &collector_id);
                continue;
            }
            let r = match self.collectors.get(&collector_id) {
                Some(_) => self.update_collector(&collector_cfg).await,
                None => self.spawn_collector(&collector_cfg).await,
            };
            if let Err(e) = r {
                log::error!("Failed to initialize collector {}: {}", &collector_id, e)
            }
        }
        //
        Ok(())
    }
    async fn spawn_collector(&mut self, config: &ZkConfigCollector) -> Result<(), AgentError> {
        log::debug!("Starting collector: {}", &config.id);
        let collector = Arc::new(Collectors::try_from(config)?);
        self.collectors
            .insert(config.id.clone(), Arc::clone(&collector));
        let collector = Arc::clone(&collector);
        tokio::spawn(async move { collector.run().await });
        Ok(())
    }
    async fn update_collector(&mut self, _config: &ZkConfigCollector) -> Result<(), AgentError> {
        return Ok(());
    }
    async fn fetch_config(&self, url: &str) -> Result<ZkConfig, AgentError> {
        let data = self.fetch_url(url).await?;
        ZkConfig::try_from(data)
    }
    async fn fetch_url(&self, url: &str) -> Result<Vec<u8>, AgentError> {
        match url.find(':') {
            Some(i) => {
                let scheme = &url[0..i];
                match scheme {
                    "file" => Self::fetch_file(&url[i + 1..url.len()]).await,
                    "http" => self.fetch_http(url).await,
                    "https" => self.fetch_http(url).await,
                    _ => Err(AgentError::FetchError("Unsupported scheme".into())),
                }
            }
            None => Err(AgentError::FetchError("Malformed URL".into())),
        }
    }
    async fn fetch_file(path: &str) -> Result<Vec<u8>, AgentError> {
        log::debug!("fetch_file: {}", path);
        let data = fs::read(path)?;
        Ok(data)
    }
    async fn fetch_http(&self, _url: &str) -> Result<Vec<u8>, AgentError> {
        Err(AgentError::NotImplementedError)
    }
}
