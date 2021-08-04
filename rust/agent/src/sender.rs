// ---------------------------------------------------------------------
// Sender implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::config::ZkConfigMetrics;
use crate::error::AgentError;
use std::cmp::min;
use std::collections::VecDeque;
use tokio::sync::mpsc;

pub enum SenderCommand {
    SetConfig(ZkConfigMetrics),
    SetKey(String),
    SetDisableCertValidation(bool),
    Send(String),
    Tick,
    Shutdown,
}

pub struct Sender {
    url: Option<String>,
    key: Option<String>,
    queue: VecDeque<String>,
    rx: mpsc::Receiver<SenderCommand>,
    tx: mpsc::Sender<SenderCommand>,
    in_tick: bool,
    // Maximal send batch size. Batch will be sent immediately if reached.
    batch_size: usize,
    // Send delay. Postpone sending of data to collect larger batch.
    send_delay_ms: u64,
    // Disable TLS certificate validation
    disable_cert_validation: bool,
    // Retry timeout, ms
    retry_timeout_ms: u64,
}

const SENDER_CHANNEL_BUFFER: usize = 10_000;
const DEFAULT_BATCH_SIZE: usize = 1_000;
const DEFAULT_SEND_DELAY: u64 = 1_000;
const DEFAULT_RETRY_TIMEOUT: u64 = 3_000;

impl Sender {
    pub fn new() -> Self {
        // @todo: Configurable buffer
        let (tx, rx) = mpsc::channel::<SenderCommand>(SENDER_CHANNEL_BUFFER);
        Self {
            url: None,
            key: None,
            queue: VecDeque::new(),
            rx,
            tx,
            in_tick: false,
            batch_size: DEFAULT_BATCH_SIZE,
            send_delay_ms: DEFAULT_SEND_DELAY,
            disable_cert_validation: false,
            retry_timeout_ms: DEFAULT_RETRY_TIMEOUT,
        }
    }
    // Get cloned tx channel
    pub fn get_tx(&self) -> mpsc::Sender<SenderCommand> {
        self.tx.clone()
    }
    // Run sender message processing
    pub async fn run(&mut self) {
        log::info!("Running sender");
        while let Some(msg) = self.rx.recv().await {
            match msg {
                SenderCommand::SetConfig(x) => self.set_config(x),
                SenderCommand::SetDisableCertValidation(x) => self.set_disable_cert_validation(x),
                SenderCommand::SetKey(x) => self.set_key(x),
                SenderCommand::Send(x) => self.enqueue(x).await,
                SenderCommand::Tick => self.on_tick().await,
                SenderCommand::Shutdown => {
                    self.drain().await;
                    break;
                }
            }
        }
        log::info!("Shutting down");
    }
    fn set_config(&mut self, cfg: ZkConfigMetrics) {
        self.set_url(cfg.url);
        self.set_batch_size(cfg.batch_size.unwrap_or(DEFAULT_BATCH_SIZE));
        self.set_send_delay_ms(cfg.send_delay_ms.unwrap_or(DEFAULT_SEND_DELAY));
        self.set_retry_timeout_ms(cfg.retry_timeout_ms.unwrap_or(DEFAULT_RETRY_TIMEOUT));
    }
    fn set_disable_cert_validation(&mut self, x: bool) {
        if x == self.disable_cert_validation {
            return; // Already set
        }
        if x {
            log::info!("Disabling certificate validation");
        } else {
            log::info!("Enabling certificate validation");
        }
        self.disable_cert_validation = x;
    }
    fn set_url(&mut self, url: String) {
        if let Some(x) = &self.url {
            if x.eq(&url) {
                return; // Already set
            }
        }
        log::info!("Set url to {}", url);
        self.url = Some(url);
    }
    fn set_key(&mut self, key: String) {
        if let Some(x) = &self.url {
            if x.eq(&key) {
                return; // Already set
            }
        }
        log::info!("Set key");
        self.key = Some(key);
    }
    fn set_batch_size(&mut self, x: usize) {
        if self.batch_size == x {
            return; // Already set
        }
        log::info!("Set batch size to {}", x);
        self.batch_size = x;
    }
    fn set_send_delay_ms(&mut self, x: u64) {
        if self.send_delay_ms == x {
            return; // Already set
        }
        log::info!("Set send delay to {}ms", x);
        self.send_delay_ms = x;
    }
    fn set_retry_timeout_ms(&mut self, x: u64) {
        if self.retry_timeout_ms == x {
            return; // Already set
        }
        log::info!("Set retry timeout to {}ms", x);
        self.retry_timeout_ms = x;
    }
    async fn on_tick(&mut self) {
        self.in_tick = false;
        self.drain().await;
    }
    fn run_tick(&mut self) {
        if self.in_tick {
            return;
        }
        self.in_tick = true;
        let tx = self.tx.clone();
        let delay_ms = self.send_delay_ms;
        tokio::spawn(async move {
            // Wait for tick interval
            tokio::time::sleep(tokio::time::Duration::from_millis(delay_ms)).await;
            // Send Tick signal
            if let Err(e) = tx.send(SenderCommand::Tick).await {
                log::info!("Cannot send tick: {}", e);
            }
        });
    }
    async fn enqueue(&mut self, msg: String) {
        // Check if url is configured
        if self.url.is_none() || self.key.is_none() {
            log::debug!("Sender is not configured. Dropped value: {}", msg);
            return;
        }
        // Enqueue, message
        self.queue.push_back(msg);
        // Start draining if necessary
        if self.queue.len() >= self.batch_size {
            self.drain().await;
        } else {
            self.run_tick();
        }
    }
    async fn drain(&mut self) {
        loop {
            let ql = self.queue.len();
            if ql == 0 {
                break;
            }
            let batch = min(ql, self.batch_size);
            log::debug!("Sending {} items", batch);
            // Convert to json
            let data = format!(
                "[{}]",
                self.queue.drain(..batch).collect::<Vec<String>>().join(",")
            );
            while let Err(e) = self.send(data.clone()).await {
                log::info!("Failed to send: {}", e);
                tokio::time::sleep(tokio::time::Duration::from_millis(self.retry_timeout_ms)).await;
                log::info!("Retry");
            }
        }
    }
    async fn send(&self, msg: String) -> Result<(), AgentError> {
        let resp = reqwest::Client::builder()
            .gzip(true)
            .danger_accept_invalid_certs(self.disable_cert_validation)
            .build()
            .map_err(|e| AgentError::InternalError(e.to_string()))?
            .post(self.url.as_ref().unwrap().clone())
            .header("Content-Type", "application/json")
            .header("X-NOC-Agent-Key", self.key.as_ref().unwrap().clone())
            .body(msg)
            .send()
            .await
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        if resp.status().is_success() {
            Ok(())
        } else {
            Err(AgentError::InternalError(format!(
                "Invalid response status: {}",
                resp.status().as_u16()
            )))
        }
    }
}

impl Default for Sender {
    fn default() -> Self {
        Self::new()
    }
}
