// ---------------------------------------------------------------------
// twamp_sender collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::{Collectable, Collector, CollectorConfig, Schedule, Status};
use super::TwampSenderOut;
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use crate::proto::connection::Connection;
use crate::proto::frame::{FrameReader, FrameWriter};
use crate::proto::pktmodel::{GetPacket, PacketModels};
use crate::proto::tos::{dscp_to_tos, tos_to_dscp};
use crate::proto::twamp::{
    AcceptSession, RequestTwSession, ServerGreeting, ServerStart, SetupResponse, StartAck,
    StartSessions, StopSessions, TestRequest, TestResponse, UtcDateTime, ACCEPT_OK, MODE_REFUSED,
    MODE_UNAUTHENTICATED,
};
use crate::timing::Timing;
use async_trait::async_trait;
use bytes::{Bytes, BytesMut};
use chrono::Utc;
use std::convert::TryFrom;
use std::net::SocketAddr;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::{
    net::{TcpStream, UdpSocket},
    time::timeout,
};

pub struct TwampSenderCollectorConfig {
    pub server: String,
    pub port: u16,
    pub n_packets: usize,
    pub model: PacketModels,
    pub tos: u8,
}

pub type TwampSenderCollector = Collector<TwampSenderCollectorConfig>;

impl TryFrom<&ZkConfigCollector> for TwampSenderCollectorConfig {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::TwampSender(config) => Ok(Self {
                server: config.server.clone(),
                port: config.port,
                n_packets: config.n_packets,
                model: PacketModels::try_from(config.model.clone())?,
                tos: dscp_to_tos(config.dscp.to_lowercase())
                    .ok_or_else(|| AgentError::ConfigurationError("invalid dscp".into()))?,
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for TwampSenderCollector {
    const NAME: &'static str = "twamp_sender";
    type Output = TwampSenderOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        //
        log::debug!(
            "[{}] Connecting {}:{}",
            self.get_id(),
            self.data.server,
            self.data.port
        );
        let stream = TcpStream::connect(format!("{}:{}", self.data.server, self.data.port)).await?;
        let ts = Self::get_timestamp();
        let out = TestSession::new(stream, self.data.model)
            .with_id(self.id.clone())
            .with_labels(self.get_labels())
            .with_tos(self.data.tos)
            .with_reflector_addr(self.data.server.clone())
            .with_n_packets(self.data.n_packets)
            .run()
            .await?;
        self.feed(ts, self.labels.clone(), &out).await?;
        Ok(Status::Ok)
    }
}

struct TestSession {
    id: String,
    labels: Option<Vec<String>>,
    connection: Connection,
    tos: u8,
    reflector_addr: String,
    reflector_port: u16,
    n_packets: usize,
    model: PacketModels,
}

impl TestSession {
    pub fn new(stream: TcpStream, model: PacketModels) -> Self {
        TestSession {
            id: String::new(),
            labels: None,
            connection: Connection::new(stream),
            tos: 0,
            reflector_addr: String::new(),
            reflector_port: 0,
            n_packets: 0,
            model,
        }
    }
    pub fn with_id(&mut self, id: String) -> &mut Self {
        self.id = id;
        self
    }
    pub fn with_labels(&mut self, labels: Vec<String>) -> &mut Self {
        self.labels = Some(labels);
        self
    }
    pub fn with_tos(&mut self, tos: u8) -> &mut Self {
        self.tos = tos;
        self
    }
    pub fn with_reflector_addr(&mut self, addr: String) -> &mut Self {
        self.reflector_addr = addr;
        self
    }
    pub fn with_n_packets(&mut self, n_packets: usize) -> &mut Self {
        self.n_packets = n_packets;
        self
    }
    pub fn set_reflector_port(&mut self, port: u16) {
        log::debug!("[{}] Setting reflector port to {}", self.id, port);
        self.reflector_port = port;
    }
    pub async fn run(&mut self) -> Result<TwampSenderOut, AgentError> {
        log::debug!("[{}] Connected", self.id);
        // Control messages timeout, 3 seconds by default
        let ctl_timeout = Duration::from_nanos(3_000_000_000);
        self.recv_server_greeting(ctl_timeout).await?;
        self.send_setup_reponse().await?;
        self.recv_server_start(ctl_timeout).await?;
        self.send_request_tw_session().await?;
        self.recv_accept_session(ctl_timeout).await?;
        self.send_start_sessions().await?;
        self.recv_start_ack(ctl_timeout).await?;
        let out = self.run_test().await?;
        self.send_stop_sessions().await?;
        Ok(out)
    }
    async fn recv_server_greeting(&mut self, t: Duration) -> Result<(), AgentError> {
        log::debug!("[{}] Waiting for Server-Greeting", self.id);
        let sg: ServerGreeting = timeout(t, self.connection.read_frame()).await??;
        log::debug!(
            "[{}] Server-Greeting received. Suggested modes: {}",
            self.id,
            sg.modes
        );
        if sg.modes == MODE_REFUSED {
            log::info!("[{}] Server refused connection. Stopping", self.id);
            return Err(AgentError::NetworkError("session refused".into()));
        }
        if sg.modes & MODE_UNAUTHENTICATED == 0 {
            log::info!("[{}] Unsupported mode. Stopping", self.id);
            return Err(AgentError::FrameError("unsupported mode".into()));
        }
        Ok(())
    }
    async fn send_setup_reponse(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Sending Setup-Response", self.id);
        let sr = SetupResponse {
            mode: MODE_UNAUTHENTICATED,
            key_id: Bytes::copy_from_slice(DEFAULT_KEY_ID),
            token: Bytes::copy_from_slice(DEFAULT_TOKEN),
            client_iv: Bytes::copy_from_slice(DEFAULT_CLIENT_IV),
        };
        self.connection.write_frame(&sr).await?;
        Ok(())
    }
    async fn recv_server_start(&mut self, t: Duration) -> Result<(), AgentError> {
        log::debug!("[{}] Waiting fot Server-Start", self.id);
        let ss: ServerStart = timeout(t, self.connection.read_frame()).await??;
        log::debug!(
            "[{}] Server-Start received. Server timestamp: {}",
            self.id,
            ss.start_time,
        );
        Ok(())
    }
    async fn send_request_tw_session(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Sending Request-TW-Session", self.id);
        let srq = RequestTwSession {
            ipvn: 4,
            padding_length: 0,
            start_time: Utc::now(),
            timeout: 255, // @todo: Make configurable
            type_p: self.tos as u32,
        };
        self.connection.write_frame(&srq).await?;
        Ok(())
    }
    async fn recv_accept_session(&mut self, t: Duration) -> Result<(), AgentError> {
        log::debug!("[{}] Waiting for Accept-Session", self.id);
        let acc_s: AcceptSession = timeout(t, self.connection.read_frame()).await??;
        log::debug!(
            "[{}] Accept-Session Received. Reflector port: {}",
            self.id,
            acc_s.port
        );
        self.set_reflector_port(acc_s.port);
        Ok(())
    }
    async fn send_start_sessions(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Sending Start-Sessions", self.id);
        let req = StartSessions {};
        self.connection.write_frame(&req).await?;
        Ok(())
    }
    async fn recv_start_ack(&mut self, t: Duration) -> Result<(), AgentError> {
        log::debug!("[{}] Waiting for Start-Ack", self.id);
        let resp: StartAck = timeout(t, self.connection.read_frame()).await??;
        if resp.accept != ACCEPT_OK {
            log::error!(
                "[{}] Failed to start session. Accept code: {}",
                self.id,
                resp.accept
            );
            return Err(AgentError::NetworkError("failed to start session".into()));
        }
        log::debug!("[{}] Start-Ack Received. Accept: {}", self.id, resp.accept);
        Ok(())
    }
    async fn send_stop_sessions(&mut self) -> Result<(), AgentError> {
        log::debug!("[{}] Sending Stop-Sessions", self.id);
        let req = StopSessions {
            accept: 0,
            num_sessions: 1,
        };
        self.connection.write_frame(&req).await?;
        Ok(())
    }
    async fn run_test(&mut self) -> Result<TwampSenderOut, AgentError> {
        log::debug!("[{}] Running test", self.id);
        let socket = UdpSocket::bind("0.0.0.0:0").await?;
        // Test request TTL must be set to 255
        socket.set_ttl(255)?;
        // @todo: Set IP_TOS
        let shared_socket = Arc::new(socket);
        let addr: SocketAddr = format!("{}:{}", self.reflector_addr, self.reflector_port)
            .parse()
            .map_err(|_| AgentError::ConfigurationError("Address parse error".into()))?;
        //
        let udp_overhead: usize = if addr.is_ipv4() { 20 + 8 } else { 40 + 8 };
        let (recv_result, sender_result) = tokio::join!(
            TestSession::run_test_receiver(
                self.id.clone(),
                shared_socket.clone(),
                self.n_packets,
                udp_overhead
            ),
            TestSession::run_test_sender(
                self.id.clone(),
                shared_socket.clone(),
                &addr,
                self.model,
                self.n_packets,
                udp_overhead
            )
        );
        if let (Ok(r_stats), Ok(s_stats)) = (recv_result, sender_result) {
            Ok(self.process_stats(s_stats, r_stats))
        } else {
            Err(AgentError::InternalError("result is not ready".to_string()))
        }
    }
    async fn run_test_sender(
        id: String,
        socket: Arc<UdpSocket>,
        addr: &SocketAddr,
        model: PacketModels,
        n_packets: usize,
        udp_overhead: usize,
    ) -> Result<SenderStats, &'static str> {
        match TestSession::test_sender(socket, addr, model, n_packets, udp_overhead).await {
            Ok(r) => Ok(r),
            Err(e) => {
                log::error!("[{}] Sender error: {}", id, e);
                Err("sender error")
            }
        }
    }
    async fn run_test_receiver(
        id: String,
        socket: Arc<UdpSocket>,
        n_packets: usize,
        udp_overhead: usize,
    ) -> Result<ReceiverStats, &'static str> {
        match TestSession::test_receiver(id.clone(), socket, n_packets, udp_overhead).await {
            Ok(r) => Ok(r),
            Err(e) => {
                log::error!("[{}] Receiver error: {}", &id, e);
                Err("receiver error")
            }
        }
    }
    #[inline]
    async fn test_sender(
        socket: Arc<UdpSocket>,
        addr: &SocketAddr,
        model: PacketModels,
        n_packets: usize,
        udp_overhead: usize,
    ) -> Result<SenderStats, AgentError> {
        let mut buf = BytesMut::with_capacity(16384);
        let mut out_octets = 0usize;
        let t0 = Instant::now();
        let mut pkt_sent = 0usize;
        let mut seq = 0usize;
        let mut now = tokio::time::Instant::now();
        let mut err_ns = 0u64;
        loop {
            let pkt = model.get_packet(seq);
            let req = TestRequest {
                seq: pkt.seq as u32,
                timestamp: Utc::now(),
                err_estimate: 0,
                pad_to: pkt.size - udp_overhead,
            };
            req.write_bytes(&mut buf)?;
            //
            out_octets += socket.send_to(&buf, addr).await? + udp_overhead;
            pkt_sent += 1;
            // Reset buffer pointer
            buf.clear();
            //
            seq += 1;
            if seq == n_packets {
                break;
            }
            //
            if pkt.next_ns == 0 {
                continue; // Flood mode
            }
            // Wait for next packet time
            if err_ns < pkt.next_ns {
                let delta_ns = pkt.next_ns - err_ns;
                tokio::time::sleep_until(now + Duration::from_nanos(delta_ns)).await;
                // As for version 1.2, Tokio timer has precision about 1ms,
                // It will lead to significant drift ever on 50pps rates.
                // so we need to add error correction to be more precise.
                let prev_now = now;
                now = tokio::time::Instant::now();
                let real_delta_ns = (now - prev_now).as_nanos() as u64;
                err_ns = real_delta_ns - delta_ns;
            } else {
                err_ns -= pkt.next_ns;
            }
        }
        Ok(SenderStats {
            pkt_sent,
            time_ns: t0.elapsed().as_nanos() as u64,
            out_octets,
        })
    }
    #[inline]
    async fn test_receiver(
        id: String,
        socket: Arc<UdpSocket>,
        n_packets: usize,
        udp_overhead: usize,
    ) -> Result<ReceiverStats, AgentError> {
        // Timeout
        let r_timeout = Duration::from_nanos(3_000_000_000);
        // Stats
        let mut pkt_received = 0usize;
        // Roundtrip/Input/Output timings
        let mut rt_timing = Timing::new();
        let mut in_timing = Timing::new();
        let mut out_timing = Timing::new();
        // Roundtrip/Input/Output loss
        let mut in_loss = 0usize;
        let mut out_loss = 0usize;
        // Roundtrip/Input/Output hops
        let mut rt_min_hops = 0xffu16;
        let mut rt_max_hops = 0u16;
        let mut in_min_hops = 0xffu8;
        let mut in_max_hops = 0u8;
        let mut out_min_hops = 0xffu8;
        let mut out_max_hops = 0u8;
        // Octets
        let mut in_octets = 0usize;
        //
        let mut buf = BytesMut::with_capacity(16384);
        let t0 = Instant::now();
        'main: for count in 0..n_packets {
            let mut ts: UtcDateTime;
            let n: usize;
            // Try to read response,
            // @todo: Replace with UDPConnection
            loop {
                match timeout(r_timeout, socket.readable()).await {
                    Ok(r) => {
                        r?;
                    }
                    Err(_) => {
                        log::info!("[{}] Receiver timed out", &id);
                        break 'main;
                    }
                }
                ts = Utc::now();
                n = match socket.try_recv_buf(&mut buf) {
                    Ok(n) => n,
                    Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                        continue;
                    }
                    Err(e) => {
                        return Err(AgentError::NetworkError(e.to_string()));
                    }
                };
                break;
            }
            // Parse request
            let resp = match TestResponse::parse(&mut buf) {
                Ok(r) => r,
                // Flood models may lead to broken frames
                Err(_) => continue,
            };
            // Reset buffer pointer
            buf.clear();
            in_octets += n + udp_overhead;
            pkt_received += 1;
            // Amount of time spent inside reflector from receiving request to building response
            let reflector_delay = resp.timestamp - resp.recv_timestamp;
            // Amount of time spend on-fly in both directions
            // Measured as delta between received response and sending request,
            // except for reflector internal delay.
            let rt_delay = ts - resp.sender_timestamp - reflector_delay;
            rt_timing.register(rt_delay.num_nanoseconds().unwrap() as u64);
            // Estimate of inbound time,
            // Delta between sender timestamp and local time
            // @todo: Apply error estimate
            let in_delay = if ts >= resp.timestamp {
                ts - resp.timestamp
            } else {
                resp.timestamp - ts
            };
            in_timing.register(in_delay.num_nanoseconds().unwrap() as u64);
            // Estimate of outbound time,
            // Delta between sender timestamp and receiver timestamp
            // @todo: Apply error estimate
            let out_delay = if resp.recv_timestamp >= resp.sender_timestamp {
                resp.recv_timestamp - resp.sender_timestamp
            } else {
                resp.sender_timestamp - resp.recv_timestamp
            };
            out_timing.register(out_delay.num_nanoseconds().unwrap() as u64);
            // Detect loss
            in_loss = resp.seq as usize - count;
            out_loss = (resp.sender_seq - resp.seq) as usize;
            // @todo: register hops properly
            let out_hops = 255 - resp.sender_ttl;
            if out_hops > out_max_hops {
                out_max_hops = out_hops
            }
            if out_hops < out_min_hops {
                out_min_hops = out_hops
            }
            let in_hops = 0u8;
            if in_hops > in_max_hops {
                in_max_hops = in_hops
            }
            if in_hops < in_min_hops {
                in_min_hops = in_hops
            }
            let rt_hops = in_hops as u16 + out_hops as u16;
            if rt_hops > rt_max_hops {
                rt_max_hops = rt_hops
            }
            if rt_hops < rt_min_hops {
                rt_min_hops = rt_hops
            }
        }
        let time_ns = t0.elapsed().as_nanos() as u64;
        rt_timing.done();
        in_timing.done();
        out_timing.done();
        let rt_loss = n_packets - pkt_received;
        Ok(ReceiverStats {
            time_ns,
            pkt_received,
            rt_timing,
            in_timing,
            out_timing,
            rt_loss,
            in_loss,
            out_loss,
            rt_min_hops,
            rt_max_hops,
            in_min_hops,
            in_max_hops,
            out_min_hops,
            out_max_hops,
            in_octets,
        })
    }
    fn humanize(v: u64) -> String {
        if v >= 10_000_000_000 {
            return format!("{:.1}G", v as f64 / 1_000_000_000.0);
        }
        if v >= 10_000_000 {
            return format!("{:.1}M", v as f64 / 1_000_000.0);
        }
        if v >= 10_000 {
            return format!("{:.1}K", v as f64 / 1_000.0);
        }
        format!("{}", v)
    }
    fn humanize_ns(v: u64) -> String {
        if v >= 10_000_000_000 {
            return format!("{:.1}s", v as f64 / 1_000_000_000.0);
        }
        if v >= 10_000_000 {
            return format!("{:.1}ms", v as f64 / 1_000_000.0);
        }
        if v >= 10_000 {
            return format!("{:.1}µs", v as f64 / 1_000.0);
        }
        format!("{}ns", v)
    }
    fn process_stats(&self, s_stats: SenderStats, r_stats: ReceiverStats) -> TwampSenderOut {
        let total = s_stats.pkt_sent as f64;
        let in_bitrate =
            (r_stats.in_octets as f64 * 8.0 / (r_stats.time_ns as f64 / 1_000_000_000.0)) as u64;
        let in_pps =
            (r_stats.pkt_received as f64 / (r_stats.time_ns as f64 / 1_000_000_000.0)) as u64;
        let out_bitrate =
            (s_stats.out_octets as f64 * 8.0 / (s_stats.time_ns as f64 / 1_000_000_000.0)) as u64;
        let out_pps = (s_stats.pkt_sent as f64 / (s_stats.time_ns as f64 / 1_000_000_000.0)) as u64;
        log::debug!(
            "Packets sent: {pkt_sent}, Packets received: {pkt_recv}, Loss: {loss}, Duration: {duration}",
            pkt_sent = s_stats.pkt_sent,
            pkt_recv = r_stats.pkt_received,
            loss=s_stats.pkt_sent - r_stats.pkt_received,
            duration=Self::humanize_ns(s_stats.time_ns),
        );
        log::debug!(
            "Out octets: {out_octets} ({out_bitrate}bit/s, {out_pps}pps), In octets: {in_octets} ({in_bitrate}bit/s, {in_pps}pps)",
            out_octets = s_stats.out_octets,
            in_octets = r_stats.in_octets,
            out_bitrate = Self::humanize(out_bitrate),
            out_pps=Self::humanize(out_pps),
            in_bitrate = Self::humanize(in_bitrate),
            in_pps=Self::humanize(in_pps),
        );
        log::debug!("Direction  | Min       | Max       | Avg       | Jitter    | Hops    | Loss");
        log::debug!(
            "-----------+-----------+-----------+-----------+-----------+---------+--------------"
        );
        log::debug!(
            "Inbound    | {min_delay:>9} | {max_delay:>9} | {avg_delay:>9} | {jitter:>9} | - | {loss:.2}%",
            min_delay = Self::humanize_ns(r_stats.in_timing.min_ns),
            max_delay = Self::humanize_ns(r_stats.in_timing.max_ns),
            avg_delay = Self::humanize_ns(r_stats.in_timing.avg_ns),
            jitter = Self::humanize_ns(r_stats.in_timing.jitter_ns),
            loss = (r_stats.in_loss as f64) * 100.0 / total,
        );
        log::debug!(
            "Outbound   | {min_delay:>9} | {max_delay:>9} | {avg_delay:>9} | {jitter:>9} | - | {loss:.2}%",
            min_delay = Self::humanize_ns(r_stats.out_timing.min_ns),
            max_delay = Self::humanize_ns(r_stats.out_timing.max_ns),
            avg_delay = Self::humanize_ns(r_stats.out_timing.avg_ns),
            jitter = Self::humanize_ns(r_stats.out_timing.jitter_ns),
            loss = (r_stats.out_loss as f64) * 100.0 / total,
        );
        log::debug!(
            "Round-Trip | {min_delay:>9} | {max_delay:>9} | {avg_delay:>9} | {jitter:>9} | - | {loss:.2}%",
            min_delay = Self::humanize_ns(r_stats.rt_timing.min_ns),
            max_delay = Self::humanize_ns(r_stats.rt_timing.max_ns),
            avg_delay = Self::humanize_ns(r_stats.rt_timing.avg_ns),
            jitter = Self::humanize_ns(r_stats.rt_timing.jitter_ns),
            loss = (r_stats.rt_loss as f64) * 100.0 / total,
        );
        // Prepare result
        let mut labels = self.labels.as_ref().unwrap().clone();
        labels.push(format!(
            "noc::dscp::{}",
            tos_to_dscp(self.tos).unwrap_or("be").to_string()
        ));
        TwampSenderOut {
            tx_packets: s_stats.pkt_sent,
            rx_packets: r_stats.pkt_received,
            tx_bytes: s_stats.out_octets,
            rx_bytes: r_stats.in_octets,
            duration_ns: s_stats.time_ns,
            tx_pps: out_pps,
            rx_pps: in_pps,
            tx_bitrate: out_bitrate,
            rx_bitrate: in_bitrate,
            // Inbound
            in_min_delay_ns: r_stats.in_timing.min_ns,
            in_max_delay_ns: r_stats.in_timing.max_ns,
            in_avg_delay_ns: r_stats.in_timing.avg_ns,
            in_jitter_ns: r_stats.in_timing.jitter_ns,
            in_loss: r_stats.in_loss,
            // Outbound
            out_min_delay_ns: r_stats.out_timing.min_ns,
            out_max_delay_ns: r_stats.out_timing.max_ns,
            out_avg_delay_ns: r_stats.out_timing.avg_ns,
            out_jitter_ns: r_stats.out_timing.jitter_ns,
            out_loss: r_stats.out_loss,
            // Round-trip
            rt_min_delay_ns: r_stats.rt_timing.min_ns,
            rt_max_delay_ns: r_stats.rt_timing.max_ns,
            rt_avg_delay_ns: r_stats.rt_timing.avg_ns,
            rt_jitter_ns: r_stats.rt_timing.jitter_ns,
            rt_loss: r_stats.rt_loss,
        }
    }
}

#[derive(Debug)]
struct SenderStats {
    pkt_sent: usize,
    time_ns: u64,
    out_octets: usize,
}

#[derive(Debug)]
struct ReceiverStats {
    time_ns: u64,
    pkt_received: usize,
    // Roundtrip/Input/Output timings
    rt_timing: Timing,
    in_timing: Timing,
    out_timing: Timing,
    // Roundtrip/Input/Output loss
    rt_loss: usize,
    in_loss: usize,
    out_loss: usize,
    // Roundtrip/Input/Output hops
    rt_min_hops: u16,
    rt_max_hops: u16,
    in_min_hops: u8,
    in_max_hops: u8,
    out_min_hops: u8,
    out_max_hops: u8,
    // Octets
    in_octets: usize,
}

// Defaults
static DEFAULT_KEY_ID: &[u8] = &[
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
];
static DEFAULT_TOKEN: &[u8] = &[
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
];
static DEFAULT_CLIENT_IV: &[u8] = &[
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
];
