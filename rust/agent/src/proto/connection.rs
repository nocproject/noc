// ---------------------------------------------------------------------
// Connection
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use crate::proto::frame::{FrameReader, FrameWriter};
use bytes::BytesMut;
use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::TcpStream,
};

#[derive(Debug)]
pub struct Connection {
    stream: TcpStream,
    in_buffer: BytesMut,
    out_buffer: BytesMut,
}

impl Connection {
    pub fn new(stream: TcpStream) -> Connection {
        if stream.set_nodelay(true).is_err() {}
        Connection {
            stream,
            in_buffer: BytesMut::with_capacity(4096),
            out_buffer: BytesMut::with_capacity(4096),
        }
    }
    pub async fn read_frame<T: FrameReader>(&mut self) -> Result<T, AgentError> {
        self.in_buffer.clear();
        loop {
            // Parse frame, if complete
            if T::is_complete(&self.in_buffer) {
                return match T::parse(&mut self.in_buffer) {
                    Ok(frame) => Ok(frame),
                    Err(e) => Err(e),
                };
            }
            // Read additional data
            if 0 == self.stream.read_buf(&mut self.in_buffer).await? {
                return Err(AgentError::NetworkError("Connection reset".into()));
            }
        }
    }
    pub async fn write_frame<T: FrameWriter>(&mut self, frame: &T) -> Result<(), AgentError> {
        self.out_buffer.clear();
        frame.write_bytes(&mut self.out_buffer)?;
        if let Err(e) = self.stream.write_all(&self.out_buffer).await {
            return Err(AgentError::NetworkError(e.to_string()));
        }
        if let Err(e) = self.stream.flush().await {
            return Err(AgentError::NetworkError(e.to_string()));
        }
        Ok(())
    }
}
