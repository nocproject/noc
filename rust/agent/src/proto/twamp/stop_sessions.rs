// ---------------------------------------------------------------------
// TWAMP Stop-Sessions
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{CMD_STOP_SESSIONS, MBZ};
use crate::proto::frame::{FrameError, FrameReader, FrameWriter};
use bytes::{Buf, BufMut, BytesMut};

/// ## Stop-Sessions structure
/// RFC-5357: 3.8
/// ```text
///  0                   1                   2                   3
///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |      3        |    Accept     |              MBZ              |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                      Number of Sessions                       |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                        MBZ (8 octets)                         |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                       HMAC (16 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// ```
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct StopSessions {
    pub accept: u8,
    pub num_sessions: u32,
}

impl FrameReader for StopSessions {
    fn min_size() -> usize {
        32
    }
    fn parse(s: &mut BytesMut) -> Result<StopSessions, FrameError> {
        // Command, 1 octet
        let cmd = s.get_u8();
        if cmd != CMD_STOP_SESSIONS {
            return Err(FrameError);
        }
        // Accept, 1 octet
        let accept = s.get_u8();
        // MBZ, 2 octets
        s.advance(2);
        // Number of sessions, 4 octets
        let num_sessions = s.get_u32();
        // MBZ, 8 octets
        // HMAC, 16 octets
        s.advance(24);
        Ok(StopSessions {
            accept,
            num_sessions,
        })
    }
}

impl FrameWriter for StopSessions {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        32
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), FrameError> {
        // Command, 1 octet
        s.put_u8(CMD_STOP_SESSIONS);
        // Accept, 1 octet
        s.put_u8(self.accept);
        // MBZ, 2 octets
        s.put_u16(0);
        // Number of sessions, 4 octets
        s.put_u32(self.num_sessions);
        // MBZ, 8 octets
        // HMAC, 16 octets
        s.put(&MBZ[..24]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::StopSessions;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use bytes::{Buf, BytesMut};

    static STOP_SESSIONS: &[u8] = &[
        0x03, // Command
        0x00, // Accept
        0x00, 0x00, // MBZ
        0x00, 0x00, 0x00, 0x01, // Num sessions
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // MBZ, 8 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // HMAC, 16 octets
    ];

    fn get_stop_sessions() -> StopSessions {
        StopSessions {
            accept: 0,
            num_sessions: 1,
        }
    }

    #[test]
    fn test_stop_sessions_min_size() {
        assert_eq!(StopSessions::min_size(), 32);
    }

    #[test]
    fn test_stop_sessions_parse() {
        let mut buf = BytesMut::from(STOP_SESSIONS);
        let expected = get_stop_sessions();
        let res = StopSessions::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert_eq!(res, Ok(expected))
    }

    #[test]
    fn test_stop_sessions_size() {
        let sg = get_stop_sessions();
        assert_eq!(sg.size(), 32)
    }

    #[test]
    fn test_stop_sessions_write_bytes() {
        let msg = get_stop_sessions();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(STOP_SESSIONS));
    }
}
