/* ---------------------------------------------------------------------
 * Agent
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2021 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::cli::CliArgs;
use crate::collectors::{Collectors, Runnable};
use crate::config::{ConfigResolver, Reader, Resolver};
use crate::config::{ZkConfig, ZkConfigCollector};
use crate::error::AgentError;
use std::collections::HashMap;
use std::convert::TryFrom;
use std::sync::Arc;
use tokio::{runtime::Runtime, task::JoinHandle};

pub struct RunningCollector {
    #[allow(dead_code)]
    collector: Arc<Collectors>,
    handle: JoinHandle<()>,
}

pub struct Agent {
    resolver: ConfigResolver,
    collectors: HashMap<String, RunningCollector>,
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
        Ok(Self {
            resolver: ConfigResolver::try_from(args)?,
            collectors: HashMap::new(),
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
                log::error!("Failed to initialize collector {}: {:?}", &collector_id, e)
            }
        }
        //
        Ok(())
    }
    async fn spawn_collector(&mut self, config: &ZkConfigCollector) -> Result<(), AgentError> {
        log::debug!("Starting collector: {}", &config.id);
        let collector = Arc::new(Collectors::try_from(config)?);
        let movable_collector = Arc::clone(&collector);
        let handle = tokio::spawn(async move { movable_collector.run().await });
        self.collectors
            .insert(config.id.clone(), RunningCollector { collector, handle });
        Ok(())
    }
    async fn update_collector(&mut self, _config: &ZkConfigCollector) -> Result<(), AgentError> {
        // @todo: Implement. May be restart new one
        return Ok(());
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
