// ---------------------------------------------------------------------
// TWAMP Server-Greeting
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::MBZ;
use crate::proto::frame::{FrameError, FrameReader, FrameWriter};
use bytes::{Buf, BufMut, Bytes, BytesMut};

/// ## Server-Greeting structure
/// RFC-4656: 3.1
/// ```text
///  0                   1                   2                   3
///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                      Unused (12 octets)                       |
/// |                                                               |
/// |+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                            Modes                              |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                     Challenge (16 octets)                     |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                        Salt (16 octets)                       |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                        Count (4 octets)                       |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                        MBZ (12 octets)                        |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// ```
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct ServerGreeting {
    pub modes: u32,
    pub challenge: Bytes,
    pub salt: Bytes,
    pub count: u32,
}

impl FrameReader for ServerGreeting {
    fn min_size() -> usize {
        64
    }
    fn parse(s: &mut BytesMut) -> Result<ServerGreeting, FrameError> {
        // MBZ, 12 octets
        s.advance(12);
        // Modes, 4 octets
        let modes = s.get_u32();
        // Challenge, 16 octets
        let challenge = s.copy_to_bytes(16);
        // Salt, 16 octets
        let salt = s.copy_to_bytes(16);
        // Count, 4 octets
        let count = s.get_u32();
        // MBZ, 12 octets
        s.advance(12);
        Ok(ServerGreeting {
            modes,
            challenge,
            salt,
            count,
        })
    }
}

impl FrameWriter for ServerGreeting {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        64
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), FrameError> {
        // MBZ, 12 octets
        s.put(&MBZ[..12]);
        // Modes, 4 octets
        s.put_u32(self.modes);
        // Challenge, 16 octets
        if self.challenge.len() != 16 {
            return Err(FrameError);
        }
        s.put(&*self.challenge);
        // Salt, 16 octets
        if self.salt.len() != 16 {
            return Err(FrameError);
        }
        s.put(&*self.salt);
        // Count, 4 octets
        s.put_u32(self.count);
        // MBZ, 12 octets
        s.put(&MBZ[..12]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::ServerGreeting;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use crate::proto::twamp::MODE_UNAUTHENTICATED;
    use bytes::{Buf, Bytes, BytesMut};

    static SERVER_GREETING1: &[u8] = &[
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // MBZ, 12 octets
        0x00, 0x00, 0x00, 0x01, // Modes, 4 octets
        0x24, 0x6a, 0xe2, 0x53, 0x2f, 0x51, 0x82, 0x3d, 0xdd, 0xdb, 0xb0, 0xa4, 0xd8, 0x3a, 0xc1,
        0x9a, // Challenge, 16 octets
        0x92, 0x31, 0x15, 0xa3, 0xbf, 0x90, 0x1a, 0x57, 0x2d, 0xdf, 0x28, 0xe8, 0xbd, 0xa7, 0x81,
        0xd6, // Salt, 16 octets
        0x00, 0x00, 0x04, 0x00, // Count, 4 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // MBZ, 12 octets
    ];

    static SERVER_GREETING1_CHALLENGE: &[u8] = &[
        0x24, 0x6a, 0xe2, 0x53, 0x2f, 0x51, 0x82, 0x3d, 0xdd, 0xdb, 0xb0, 0xa4, 0xd8, 0x3a, 0xc1,
        0x9a,
    ];
    static SERVER_GREETING1_SALT: &[u8] = &[
        0x92, 0x31, 0x15, 0xa3, 0xbf, 0x90, 0x1a, 0x57, 0x2d, 0xdf, 0x28, 0xe8, 0xbd, 0xa7, 0x81,
        0xd6,
    ];

    fn get_server_greeting() -> ServerGreeting {
        ServerGreeting {
            modes: MODE_UNAUTHENTICATED,
            challenge: Bytes::from_static(&SERVER_GREETING1_CHALLENGE),
            salt: Bytes::from_static(&SERVER_GREETING1_SALT),
            count: 1024,
        }
    }

    #[test]
    fn test_server_greeting_min_size() {
        assert_eq!(ServerGreeting::min_size(), 64);
    }

    #[test]
    fn test_server_greeting_parse() {
        let mut buf = BytesMut::from(SERVER_GREETING1);
        let expected = get_server_greeting();
        let res = ServerGreeting::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert_eq!(res, Ok(expected))
    }

    #[test]
    fn test_server_greeting_size() {
        let sg = get_server_greeting();
        assert_eq!(sg.size(), 64)
    }

    #[test]
    fn test_server_greeting_write_bytes() {
        let msg = get_server_greeting();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(SERVER_GREETING1));
    }
}
