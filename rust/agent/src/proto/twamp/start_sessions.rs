// ---------------------------------------------------------------------
// TWAMP Start-Sessions
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{CMD_START_SESSIONS, MBZ};
use crate::error::AgentError;
use crate::proto::frame::{FrameReader, FrameWriter};
use bytes::{Buf, BufMut, BytesMut};

/// ## Start-Sessions structure
/// RFC-4656: 3.5
/// ```text
///  0                   1                   2                   3
///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |      2        |                                               |
/// +-+-+-+-+-+-+-+-+                                               |
/// |                        MBZ (15 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                       HMAC (16 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+/
/// ```
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct StartSessions {}

impl FrameReader for StartSessions {
    fn min_size() -> usize {
        32
    }
    fn parse(s: &mut BytesMut) -> Result<StartSessions, AgentError> {
        // Command, 1 octet
        let cmd = s.get_u8();
        if cmd != CMD_START_SESSIONS {
            return Err(AgentError::FrameError("Invalid command".into()));
        }
        // MBZ, 15 octets
        // HMAC, 16 octets
        s.advance(31);
        Ok(StartSessions {})
    }
}

impl FrameWriter for StartSessions {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        32
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), AgentError> {
        // Command, 1 octet
        s.put_u8(CMD_START_SESSIONS);
        // MBZ, 15 octets
        // HMAC, 16 octets
        s.put(&MBZ[..31]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::StartSessions;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use bytes::{Buf, BytesMut};

    static START_SESSIONS: &[u8] = &[
        0x02, // Command
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // MBZ, 15 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // MBZ, 16 octets
    ];

    fn get_start_sessions() -> StartSessions {
        StartSessions {}
    }

    #[test]
    fn test_start_sessions_min_size() {
        assert_eq!(StartSessions::min_size(), 32);
    }

    #[test]
    fn test_start_sessions_parse() {
        let mut buf = BytesMut::from(START_SESSIONS);
        let expected = get_start_sessions();
        let res = StartSessions::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert!(res.is_ok());
        assert_eq!(res.unwrap(), expected);
    }

    #[test]
    fn test_start_sessions_size() {
        let sg = get_start_sessions();
        assert_eq!(sg.size(), 32)
    }

    #[test]
    fn test_start_sessions_write_bytes() {
        let msg = get_start_sessions();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(START_SESSIONS));
    }
}
