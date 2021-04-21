// ---------------------------------------------------------------------
// FrameReader and FrameWriter traits
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use bytes::{Bytes, BytesMut};

pub trait FrameReader: Sized {
    /// Minimal size of frame
    fn min_size() -> usize;
    /// Check input buffer has complete frame
    fn is_complete(buffer: &BytesMut) -> bool {
        buffer.len() >= Self::min_size()
    }
    /// Read and parse full frame from buffer
    fn parse(s: &mut BytesMut) -> Result<Self, AgentError>;
}

pub trait FrameWriter {
    /// Get size of serialized frame
    fn size(&self) -> usize;
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), AgentError>;
    /// Return new buffer containing serialized frame
    fn as_bytes(&self) -> Result<Bytes, AgentError> {
        let mut buf = BytesMut::with_capacity(self.size());
        self.write_bytes(&mut buf)?;
        Ok(buf.freeze())
    }
}
