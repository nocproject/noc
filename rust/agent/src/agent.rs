/* ---------------------------------------------------------------------
 * Agent
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2021 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::cli::CliArgs;
use crate::collectors::{Collectors, MetricSender, Runnable};
use crate::config::{ConfigResolver, Reader, Resolver};
use crate::config::{ZkConfig, ZkConfigCollector};
use crate::error::AgentError;
use crate::sender::{Sender, SenderCommand};
use std::collections::{hash_map::DefaultHasher, HashMap, HashSet};
use std::convert::TryFrom;
use std::hash::{Hash, Hasher};
use std::sync::Arc;
use tokio::{runtime::Runtime, sync::mpsc, task::JoinHandle};

pub struct RunningCollector {
    #[allow(dead_code)]
    collector: Arc<Collectors>,
    handle: JoinHandle<()>,
    cfg_hash: u64,
}

pub struct Agent {
    resolver: ConfigResolver,
    collectors: HashMap<String, RunningCollector>,
    sender_tx: Option<mpsc::Sender<SenderCommand>>,
    disable_cert_validation: bool,
}

impl TryFrom<CliArgs> for Agent {
    type Error = AgentError;

    fn try_from(args: CliArgs) -> Result<Self, Self::Error> {
        // Init logging
        env_logger::builder()
            .format_timestamp_millis()
            .filter_level(if args.verbose {
                log::LevelFilter::Debug
            } else {
                log::LevelFilter::Info
            })
            .init();
        // Build agent
        let disable_cert_validation = args.disable_cert_validation;
        Ok(Self {
            resolver: ConfigResolver::try_from(args)?,
            collectors: HashMap::new(),
            sender_tx: None,
            disable_cert_validation,
        })
    }
}

impl Agent {
    pub fn run(&mut self) -> Result<(), AgentError> {
        log::info!("Running agent");
        let runtime = Runtime::new()?;
        runtime.block_on(async move { self.bootstrap().await })?;
        log::info!("Stopping agent");
        Ok(())
    }

    async fn bootstrap(&mut self) -> Result<(), AgentError> {
        self.resolver.bootstrap().await?;
        // Spawn sender
        let mut sender = Sender::new();
        self.sender_tx = Some(sender.get_tx());
        tokio::spawn(async move {
            sender.run().await;
        });
        //
        loop {
            let reader = self.resolver.get_reader()?;
            let status = match reader.get_config().await {
                Ok(conf) => {
                    self.resolver.apply(&conf)?;
                    self.apply(&conf).await?;
                    true
                }
                Err(e) => {
                    log::info!("Cannot read config: {:?}", e);
                    if !self.resolver.is_failable() {
                        // Fatal error, cannot be restarted
                        return Err(e);
                    }
                    false
                }
            };
            if !self.resolver.is_repeatable() {
                // Wait until all collectors to stop
                self.wait_all().await?;
                break; // Stop config refreshing
            }
            self.resolver.sleep(status).await;
        }
        Ok(())
    }
    async fn apply(&mut self, cfg: &ZkConfig) -> Result<(), AgentError> {
        // Configure sender
        if let Some(tx) = &self.sender_tx {
            // Cert validation
            tx.send(SenderCommand::SetDisableCertValidation(
                self.disable_cert_validation,
            ))
            .await
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
            // key
            if let Some(key) = &cfg.config.zeroconf.key {
                tx.send(SenderCommand::SetKey(key.clone()))
                    .await
                    .map_err(|e| AgentError::InternalError(e.to_string()))?;
            }
            // config
            if let Some(x) = &cfg.config.metrics {
                tx.send(SenderCommand::SetConfig(x.clone()))
                    .await
                    .map_err(|e| AgentError::InternalError(e.to_string()))?;
            }
        }
        // Configure collectors
        let mut id_set = HashSet::new();
        for collector_cfg in cfg.collectors.iter() {
            let collector_id: String = String::from(&collector_cfg.id);
            if collector_cfg.disabled {
                log::debug!("[{}] Collector is disabled", &collector_id);
                continue;
            }
            let r = match self.collectors.get(&collector_id) {
                Some(_) => self.update_collector(collector_cfg).await,
                None => self.spawn_collector(collector_cfg).await,
            };
            if let Err(e) = r {
                log::error!("Failed to initialize collector {}: {:?}", &collector_id, e)
            }
            id_set.insert(&collector_cfg.id);
        }
        // Stop unused collectors
        let mut stop_set = HashSet::new();
        for x in self.collectors.keys() {
            if !id_set.contains(x) {
                stop_set.insert(x.clone());
            }
        }
        for x in stop_set.iter() {
            self.stop_collector(x).await?;
        }
        Ok(())
    }
    // Start new collector instance
    async fn spawn_collector(&mut self, config: &ZkConfigCollector) -> Result<(), AgentError> {
        log::debug!("[{}] Starting collector", &config.id);
        let mut c = Collectors::try_from(config)?;
        if let Some(tx) = &self.sender_tx {
            c.with_sender_tx(tx.clone());
        }
        let cfg_hash = Self::cfg_hash(config);
        let collector = Arc::new(c);
        let movable_collector = Arc::clone(&collector);
        let handle = tokio::spawn(async move { movable_collector.run().await });
        self.collectors.insert(
            config.id.clone(),
            RunningCollector {
                collector,
                handle,
                cfg_hash,
            },
        );
        Ok(())
    }
    // Stop running collector
    async fn stop_collector(&mut self, collector_id: &str) -> Result<(), AgentError> {
        log::debug!("[{}] Stopping", collector_id);
        if let Some(c) = self.collectors.remove(collector_id) {
            c.handle.abort();
        }
        Ok(())
    }
    // Update running collector configuration
    async fn update_collector(&mut self, config: &ZkConfigCollector) -> Result<(), AgentError> {
        if let Some(collector) = self.collectors.get(&config.id) {
            let cfg_hash = Self::cfg_hash(config);
            if cfg_hash != collector.cfg_hash {
                // Config changed, restart
                log::debug!("[{}] Configuration changed, restarting", &config.id);
                self.stop_collector(&config.id).await?;
                self.spawn_collector(config).await?;
            }
        }
        Ok(())
    }
    // Calculate stable config hash to detect changes
    fn cfg_hash(config: &ZkConfigCollector) -> u64 {
        let mut hasher = DefaultHasher::new();
        config.hash(&mut hasher);
        hasher.finish()
    }
    // Wait for all running collectors to complete
    async fn wait_all(&mut self) -> Result<(), AgentError> {
        for (_id, c) in self.collectors.drain() {
            c.handle
                .await
                .map_err(|e| AgentError::InternalError(e.to_string()))?;
        }
        Ok(())
    }
}
