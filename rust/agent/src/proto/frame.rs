// ---------------------------------------------------------------------
// FrameReader and FrameWriter traits
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use bytes::{Bytes, BytesMut};
use std::error::Error;

#[derive(Clone, PartialEq, Debug)]
pub struct FrameError;

impl std::fmt::Display for FrameError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "frame error")
    }
}

impl Error for FrameError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        None
    }
}

impl From<std::io::Error> for FrameError {
    fn from(_: std::io::Error) -> FrameError {
        FrameError
    }
}

pub trait FrameReader: Sized {
    /// Minimal size of frame
    fn min_size() -> usize;
    /// Check input buffer has complete frame
    fn is_complete(buffer: &BytesMut) -> bool {
        buffer.len() >= Self::min_size()
    }
    /// Read and parse full frame from buffer
    fn parse(s: &mut BytesMut) -> Result<Self, FrameError>;
}

pub trait FrameWriter {
    /// Get size of serialized frame
    fn size(&self) -> usize;
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), FrameError>;
    /// Return new buffer containing serialized frame
    fn as_bytes(&self) -> Result<Bytes, FrameError> {
        let mut buf = BytesMut::with_capacity(self.size());
        self.write_bytes(&mut buf)?;
        Ok(buf.freeze())
    }
}
