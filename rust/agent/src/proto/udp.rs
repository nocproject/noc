// ---------------------------------------------------------------------
// UDP utilities
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::proto::frame::{FrameReader, FrameWriter};
use bytes::BytesMut;
use std::error::Error;
use std::net::SocketAddr;
use tokio::net::{ToSocketAddrs, UdpSocket};

#[derive(Debug)]
pub struct UdpConnection {
    socket: UdpSocket,
    buffer: BytesMut,
}

const UDP_BUFF_CAPACITY: usize = 16384;

impl UdpConnection {
    pub async fn bind<A: ToSocketAddrs>(addr: A) -> std::io::Result<UdpConnection> {
        let socket = UdpSocket::bind(addr).await?;
        Ok(UdpConnection {
            socket,
            buffer: BytesMut::with_capacity(UDP_BUFF_CAPACITY),
        })
    }
    pub fn local_port(&self) -> Result<u16, Box<dyn Error>> {
        Ok(self.socket.local_addr()?.port())
    }
    pub fn set_ttl(&self, ttl: u32) -> Result<(), Box<dyn Error>> {
        self.socket.set_ttl(ttl)?;
        Ok(())
    }
    pub async fn recv_from<T: FrameReader>(&mut self) -> Result<(T, SocketAddr), Box<dyn Error>> {
        self.buffer.clear();
        loop {
            self.socket.readable().await?;
            match self.socket.try_recv_buf_from(&mut self.buffer) {
                Ok((_, addr)) => {
                    let r = T::parse(&mut self.buffer)?;
                    return Ok((r, addr));
                }
                Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                    continue;
                }
                Err(e) => {
                    return Err(Box::new(e));
                }
            }
        }
    }
    pub async fn send_to<T: FrameWriter>(
        &mut self,
        frame: &T,
        addr: SocketAddr,
    ) -> Result<(), Box<dyn Error>> {
        self.buffer.clear();
        frame.write_bytes(&mut self.buffer)?;
        self.socket.send_to(&self.buffer, addr).await?;
        Ok(())
    }
}
