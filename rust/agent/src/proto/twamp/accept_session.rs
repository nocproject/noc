// ---------------------------------------------------------------------
// TWAMP Accept-Session
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::MBZ;
use crate::proto::frame::{FrameError, FrameReader, FrameWriter};
use bytes::{Buf, BufMut, BytesMut};

/// ## Accept-Session structure
/// RFC-4656: 3.5
/// ```text
/// 0                   1                   2                   3
///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |    Accept     |  MBZ          |            Port               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
/// |                                                               |
/// |                        SID (16 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                        MBZ (12 octets)                        |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                       HMAC (16 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// ```
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct AcceptSession {
    pub accept: u8,
    pub port: u16,
}

impl FrameReader for AcceptSession {
    fn min_size() -> usize {
        48
    }
    fn parse(s: &mut BytesMut) -> Result<AcceptSession, FrameError> {
        // Accept, 1 octet
        let accept = s.get_u8();
        // MBZ, 1 octet
        s.advance(1);
        // Port, 2 octets
        let port = s.get_u16();
        // SID, 16 octets
        // MBZ, 12 octets
        // HMAC, 16 octets
        // 44 total
        s.advance(44);
        Ok(AcceptSession { accept, port })
    }
}

impl FrameWriter for AcceptSession {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        48
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), FrameError> {
        // Accept, 1 octet
        s.put_u8(self.accept);
        // MBZ, 1 octet
        s.put_u8(0);
        // Port, 2 octets
        s.put_u16(self.port);
        // SID, 16 octets
        // MBZ, 12 octets
        // HMAC, 16 octets
        // 44 total
        s.put(&MBZ[..44]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::AcceptSession;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use bytes::{Buf, BytesMut};

    static ACCEPT_SESSION: &[u8] = &[
        0x00, // Accept
        0x00, // MBZ
        0xbb, 0x80, // Port
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // SID, 16 octet
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // MBZ, 12 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // HMAC, 16 octets
    ];

    fn get_accept_session() -> AcceptSession {
        AcceptSession {
            accept: 0,
            port: 48000,
        }
    }

    #[test]
    fn test_accept_session_min_size() {
        assert_eq!(AcceptSession::min_size(), 48);
    }

    #[test]
    fn test_accept_session_parse() {
        let mut buf = BytesMut::from(ACCEPT_SESSION);
        let expected = get_accept_session();
        let res = AcceptSession::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert_eq!(res, Ok(expected))
    }

    #[test]
    fn test_accept_session_size() {
        let sg = get_accept_session();
        assert_eq!(sg.size(), 48)
    }

    #[test]
    fn test_accept_session_write_bytes() {
        let msg = get_accept_session();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(ACCEPT_SESSION));
    }
}
