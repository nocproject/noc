// ---------------------------------------------------------------------
// twamp_reflector collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{CollectorConfig, Id, Runnable};
use crate::error::AgentError;
use crate::proto::connection::Connection;
use crate::proto::twamp::{
    AcceptSession, RequestTwSession, ServerGreeting, ServerStart, SetupResponse, StartAck,
    StartSessions, StopSessions, TestRequest, TestResponse, DEFAULT_COUNT, MODE_UNAUTHENTICATED,
};
use crate::proto::udp::UdpConnection;
use crate::zk::ZkConfigCollector;
use agent_derive::Id;
use async_trait::async_trait;
use bytes::Bytes;
use chrono::Utc;
use rand::Rng;
use std::convert::TryFrom;
use std::net::SocketAddr;
use std::time::Duration;
use tokio::{
    net::{TcpListener, TcpStream},
    sync::oneshot,
    time::timeout,
};

#[derive(Id)]
pub struct TwampReflectorCollector {
    pub id: String,
    pub listen: String,
    pub port: u16,
}

impl TryFrom<&ZkConfigCollector> for TwampReflectorCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::TwampReflector(config) => Ok(Self {
                id: value.id.clone(),
                listen: config.listen.clone(),
                port: config.port,
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[derive(Debug)]
struct ClientSession {
    id: String,
    connection: Connection,
    addr: SocketAddr,
    dscp: u8,
    reflector_port: Option<u16>,
}

#[async_trait]
impl Runnable for TwampReflectorCollector {
    async fn run(&self) {
        log::debug!("[{}] Starting collector", self.id);
        let r = TcpListener::bind(format!("{}:{}", self.listen, self.port)).await;
        if let Err(e) = r {
            log::error!(
                "[{}] Failed to create listener {}:{}: {}",
                self.id,
                self.listen,
                self.port,
                e
            );
            return;
        }
        let listener = r.unwrap();
        log::info!("[{}] Listening {}:{}", self.id, self.listen, self.port);
        loop {
            match listener.accept().await {
                Ok((stream, addr)) => {
                    // Clone id to prevent moving of self
                    let id = self.id.clone();
                    // Span client session
                    tokio::spawn(async move {
                        let mut session = ClientSession::new_from(id, stream, addr);
                        session.run().await;
                    });
                }
                Err(e) => {
                    log::error!("[{}] Failed to accept connection: {}", self.id, e);
                }
            }
        }
    }
}

impl ClientSession {
    fn new_from(id: String, stream: TcpStream, addr: SocketAddr) -> ClientSession {
        ClientSession {
            id,
            connection: Connection::new(stream),
            addr,
            dscp: 0,
            reflector_port: None,
        }
    }

    async fn run(&mut self) {
        if let Err(e) = self.process().await {
            log::error!(
                "[{}][{}] Failed to process session: {}",
                self.id,
                self.addr,
                e
            )
        }
    }

    async fn process(&mut self) -> Result<(), AgentError> {
        log::info!("[{}][{}] Connected", self.id, self.addr);
        // Control messages timeout, 3 seconds by default
        let ctl_timeout = Duration::from_nanos(3_000_000_000);
        self.send_server_greeting().await?;
        self.recv_setup_response(ctl_timeout).await?;
        self.send_server_start().await?;
        self.recv_request_tw_session(ctl_timeout).await?;
        self.start_reflector().await?;
        self.send_accept_session().await?;
        self.recv_start_sessions(ctl_timeout).await?;
        self.send_start_ack().await?;
        self.recv_stop_sessions().await?; // No direct timeout
        log::info!("[{}][{}] Session complete", self.id, self.addr);
        Ok(())
    }
    async fn send_server_greeting(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}][{}] Sending Server-Greeting", self.id, self.addr);
        // Send Server-Greeting
        let challenge = rand::thread_rng().gen::<[u8; 16]>();
        let salt = rand::thread_rng().gen::<[u8; 16]>();
        let sg = ServerGreeting {
            modes: MODE_UNAUTHENTICATED,
            challenge: Bytes::copy_from_slice(&challenge),
            salt: Bytes::copy_from_slice(&salt),
            count: DEFAULT_COUNT,
        };
        self.connection.write_frame(&sg).await?;
        Ok(())
    }
    async fn recv_setup_response(&mut self, t: Duration) -> Result<(), AgentError> {
        log::debug!("[{}] Waiting for Setup-Response", self.id);
        let sr: SetupResponse = timeout(t, self.connection.read_frame()).await??;
        log::debug!("[{}] Received Setup-Response", self.id);
        match sr.mode {
            MODE_UNAUTHENTICATED => self.auth_unathenticated().await,
            _ => {
                log::error!("[{}] Unsupported mode: {}", self.id, sr.mode);
                Err(AgentError::FrameError("unsupported mode".into()))
            }
        }
    }
    async fn auth_unathenticated(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Starting unauthenticated session", self.id);
        Ok(())
    }

    async fn send_server_start(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Sending Server-Start", self.id);
        let server_iv = rand::thread_rng().gen::<[u8; 16]>();
        let ss = ServerStart {
            accept: 0,
            server_iv: Bytes::copy_from_slice(&server_iv),
            start_time: Utc::now(),
        };
        self.connection.write_frame(&ss).await?;
        Ok(())
    }
    async fn recv_request_tw_session(&mut self, t: Duration) -> Result<(), AgentError> {
        log::debug!("[{}] Waiting for Request-TW-Session", self.id);
        let req: RequestTwSession = timeout(t, self.connection.read_frame()).await??;
        log::debug!(
            "[{}] Received Request-TW-Session. Client timestamp={:?}, Type-P={}",
            self.id,
            req.start_time,
            req.type_p
        );
        self.dscp = (req.type_p & 0xff) as u8;
        Ok(())
    }
    async fn send_accept_session(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Sending Accept-Session", self.id);
        let msg = AcceptSession {
            accept: 0,
            port: self.get_reflector_port()?,
        };
        self.connection.write_frame(&msg).await?;
        Ok(())
    }
    async fn recv_start_sessions(&mut self, t: Duration) -> Result<(), AgentError> {
        log::debug!("[{}] Waiting for Start-Sessions", self.id);
        let _: StartSessions = timeout(t, self.connection.read_frame()).await??;
        log::debug!("[{}] Start-Sessions received", self.id);
        Ok(())
    }
    async fn send_start_ack(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Sending Start-Ack", self.id);
        let msg = StartAck { accept: 0 };
        self.connection.write_frame(&msg).await?;
        Ok(())
    }
    async fn recv_stop_sessions(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Waiting for Stop-Sessions", self.id);
        let _: StopSessions = self.connection.read_frame().await?;
        log::debug!("[{}] Received Stop-Sessions", self.id,);
        Ok(())
    }
    fn get_reflector_port(&self) -> Result<u16, AgentError> {
        match self.reflector_port {
            Some(port) => Ok(port),
            None => Err(AgentError::NetworkError("socket not created".into())),
        }
    }
    async fn start_reflector(&mut self) -> Result<(), AgentError> {
        let id = self.id.clone();
        let (tx, rx) = oneshot::channel();
        tokio::spawn(async move {
            if let Err(e) = ClientSession::reflect(id.clone(), tx).await {
                log::error!("[{} Reflector error: {:?}", id, e);
            }
        });
        match rx.await {
            Ok(x) => self.reflector_port = Some(x),
            Err(e) => {
                log::error!("[{}] Reflector error: {}", self.id, e);
                return Err(AgentError::NetworkError(e.to_string()));
            }
        }
        Ok(())
    }
    async fn reflect(id: String, port_channel: oneshot::Sender<u16>) -> Result<(), AgentError> {
        log::debug!("[{}] Creating reflector", id);
        // Timeout
        let recv_timeout = Duration::from_nanos(3_000_000_000);
        // Reflector socket
        let mut socket = UdpConnection::bind("0.0.0.0:0").await?;
        // Reflector TTL must be set to 255
        socket.set_ttl(255)?;
        // Send back allocated port to session
        if let Err(e) = port_channel.send(socket.local_port()?) {
            log::error!("[{}] Cannot send reflector port: {}", id, e);
            return Err(AgentError::NetworkError(
                "cannot send reflector port".into(),
            ));
        }
        //
        let mut seq = 0u32;
        loop {
            let (req, addr) = match timeout(recv_timeout, socket.recv_from::<TestRequest>()).await {
                Ok(Ok(r)) => r,
                // recv_from returns an error
                // We'd expected truncated frames on high load, so count it as a loss
                Ok(Err(_)) => continue,
                // Timed out, break the loop
                Err(_) => break,
            };
            // Build response
            let ts = Utc::now();
            let resp = TestResponse {
                seq,
                timestamp: ts,
                err_estimate: 0,
                recv_timestamp: ts,
                sender_seq: req.seq,
                sender_timestamp: req.timestamp,
                sender_err_estimate: req.err_estimate,
                sender_ttl: 255, // @todo: Get real TTL
                pad_to: req.pad_to,
            };
            //
            socket.send_to(&resp, addr).await?;
            seq += 1;
        }
        log::debug!("[{}] Stopping reflector", id);
        Ok(())
    }
}
