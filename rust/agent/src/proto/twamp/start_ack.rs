// ---------------------------------------------------------------------
// Start-Ack structure
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::MBZ;
use crate::proto::frame::{FrameError, FrameReader, FrameWriter};
use bytes::{Buf, BufMut, BytesMut};

/// ## Start-Ack structure
/// RFC-4656: 3.5
/// ```text
///  0                   1                   2                   3
///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |     Accept    |                                               |
/// +-+-+-+-+-+-+-+-+                                               |
/// |                        MBZ (15 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                       HMAC (16 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// ```
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct StartAck {
    pub accept: u8,
}

impl FrameReader for StartAck {
    fn min_size() -> usize {
        32
    }
    fn parse(s: &mut BytesMut) -> Result<StartAck, FrameError> {
        // Accept, 1 octet
        let accept = s.get_u8();
        // MBZ, 15 octets
        // HMAC, 16 octets
        s.advance(31);
        Ok(StartAck { accept })
    }
}

impl FrameWriter for StartAck {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        32
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), FrameError> {
        // Accept, 1 octet
        s.put_u8(self.accept);
        // MBZ, 15 octets
        // HMAC, 16 octets
        s.put(&MBZ[..31]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::StartAck;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use bytes::{Buf, BytesMut};

    static START_ACK: &[u8] = &[
        0x00, // Accept
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // MBZ, 15 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // MBZ, 16 octets
    ];

    fn get_start_sessions() -> StartAck {
        StartAck { accept: 0 }
    }

    #[test]
    fn test_start_ack_min_size() {
        assert_eq!(StartAck::min_size(), 32);
    }

    #[test]
    fn test_start_ack_parse() {
        let mut buf = BytesMut::from(START_ACK);
        let expected = get_start_sessions();
        let res = StartAck::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert_eq!(res, Ok(expected))
    }

    #[test]
    fn test_start_ack_size() {
        let sg = get_start_sessions();
        assert_eq!(sg.size(), 32)
    }

    #[test]
    fn test_start_ack_write_bytes() {
        let msg = get_start_sessions();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(START_ACK));
    }
}
