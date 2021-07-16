// ---------------------------------------------------------------------
// TWAMP Server-Start
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{NtpTimeStamp, UtcDateTime, MBZ};
use crate::error::AgentError;
use crate::proto::frame::{FrameReader, FrameWriter};
use bytes::{Buf, BufMut, Bytes, BytesMut};

/// ## Server-Start structure
/// ```text
///  0                   1                   2                   3
///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                         MBZ (15 octets)                       |
/// |                                                               |
/// |                                               +-+-+-+-+-+-+-+-+
/// |                                               |   Accept      |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                     Server-IV (16 octets)                     |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                     Start-Time (Timestamp)                    |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                         MBZ (8 octets)                        |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// ```
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct ServerStart {
    pub accept: u8,
    pub server_iv: Bytes,
    pub start_time: UtcDateTime,
}

impl FrameReader for ServerStart {
    fn min_size() -> usize {
        48
    }
    fn parse(s: &mut BytesMut) -> Result<ServerStart, AgentError> {
        // MBZ, 15 octets
        s.advance(15);
        // Accept, 1 octet
        let accept = s.get_u8();
        // Server-IV, 16 octets
        let server_iv = s.copy_to_bytes(16);
        // Start-Time, 8 octets
        let ts = NtpTimeStamp::new(s.get_u32(), s.get_u32());
        // MBZ, 8 octets
        s.advance(8);
        //
        Ok(ServerStart {
            accept,
            server_iv,
            start_time: ts.into(),
        })
    }
}

impl FrameWriter for ServerStart {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        48
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), AgentError> {
        // MBZ, 15 octets
        s.put(&MBZ[..15]);
        // Accept, 1 octet
        s.put_u8(self.accept);
        // Server-IV, 16 octets
        if self.server_iv.len() != 16 {
            return Err(AgentError::FrameError(
                "Server-IV must be of 16 octets".into(),
            ));
        }
        s.put(&*self.server_iv);
        // Start-Time, 8 octets
        let ts: NtpTimeStamp = self.start_time.into();
        s.put_u32(ts.secs());
        s.put_u32(ts.fracs());
        // MBZ, 8 octets
        s.put(&MBZ[..8]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::ServerStart;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use bytes::{Buf, Bytes, BytesMut};
    use chrono::{TimeZone, Utc};

    static SERVER_START: &[u8] = &[
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // MBZ, 15 octets
        0x00, // Accept, 1 octet
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e,
        0x0f, // Server-IV, 16 octets
        0xe3, 0xd0, 0xd0, 0x20, 0x00, 0x00, 0x00, 0x00, // Server time, 8 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // MBZ, 8 octets
    ];

    static SERVER_IV: &[u8] = &[
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e,
        0x0f,
    ];

    fn get_server_start() -> ServerStart {
        ServerStart {
            accept: 0,
            server_iv: Bytes::from_static(SERVER_IV),
            start_time: Utc.ymd(2021, 2, 12).and_hms(10, 0, 0),
        }
    }

    #[test]
    fn test_server_start_min_size() {
        assert_eq!(ServerStart::min_size(), 48);
    }

    #[test]
    fn test_server_start_parse() {
        let mut buf = BytesMut::from(SERVER_START);
        let expected = get_server_start();
        let res = ServerStart::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert!(res.is_ok());
        assert_eq!(res.unwrap(), expected);
    }

    #[test]
    fn test_server_start_size() {
        let sg = get_server_start();
        assert_eq!(sg.size(), 48)
    }

    #[test]
    fn test_server_start_write_bytes() {
        let msg = get_server_start();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(SERVER_START));
    }
}
