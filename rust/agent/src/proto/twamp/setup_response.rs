// ---------------------------------------------------------------------
// TWAMP Setup-Response
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::proto::frame::{FrameError, FrameReader, FrameWriter};
use bytes::{Buf, BufMut, Bytes, BytesMut};

/// ## Setup-Response structure
/// RFC-4656: 3.1
/// ```text
///  0                   1                   2                   3
///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                             Mode                              |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// .                                                               .
/// .                       KeyID (80 octets)                       .
/// .                                                               .
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// .                                                               .
/// .                       Token (64 octets)                       .
/// .                                                               .
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// .                                                               .
/// .                     Client-IV (16 octets)                     .
/// .                                                               .
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-/
/// ```
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct SetupResponse {
    pub mode: u32,
    pub key_id: Bytes,
    pub token: Bytes,
    pub client_iv: Bytes,
}

impl FrameReader for SetupResponse {
    fn min_size() -> usize {
        164
    }
    fn parse(s: &mut BytesMut) -> Result<Self, FrameError> {
        // Mode, 4 octets
        let mode = s.get_u32();
        // Key ID, 80 octets
        let key_id = s.copy_to_bytes(80);
        // Token, 64 octets
        let token = s.copy_to_bytes(64);
        // Client IV: 16 octets
        let client_iv = s.copy_to_bytes(16);
        Ok(SetupResponse {
            mode,
            key_id,
            token,
            client_iv,
        })
    }
}

impl FrameWriter for SetupResponse {
    fn size(&self) -> usize {
        164
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), FrameError> {
        // Mode, 4 octets
        s.put_u32(self.mode);
        // Key ID, 80 octets
        if self.key_id.len() != 80 {
            return Err(FrameError);
        }
        s.put(&*self.key_id);
        // Token, 64 octets
        if self.token.len() != 64 {
            return Err(FrameError);
        }
        s.put(&*self.token);
        // Client IV: 16 octets
        if self.client_iv.len() != 16 {
            return Err(FrameError);
        }
        s.put(&*self.client_iv);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::SetupResponse;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use crate::proto::twamp::MODE_UNAUTHENTICATED;
    use bytes::{Bytes, BytesMut};

    static SETUP_RESPONSE1: &[u8] = &[
        0x00, 0x00, 0x00, 0x01, // Modes, 4 octets
        0x74, 0x65, 0x73, 0x74, 0x2d, 0x6b, 0x65, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, // Key-Id, 80 octets
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e,
        0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d,
        0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c,
        0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b,
        0x3c, 0x3d, 0x3e, 0x3f, // Token, 64 octets
        0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e,
        0x8, // Client-IV, 16 octets
    ];

    static SETUP_RESPONSE1_KEY_ID: &[u8] = &[
        0x74, 0x65, 0x73, 0x74, 0x2d, 0x6b, 0x65, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00,
    ];

    static SETUP_RESPONSE1_TOKEN: &[u8] = &[
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e,
        0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d,
        0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c,
        0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b,
        0x3c, 0x3d, 0x3e, 0x3f,
    ];

    static SETUP_RESPONSE1_CLIENT_IV: &[u8] = &[
        0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e,
        0x8,
    ];

    fn get_setup_response() -> SetupResponse {
        SetupResponse {
            mode: MODE_UNAUTHENTICATED,
            key_id: Bytes::from_static(SETUP_RESPONSE1_KEY_ID),
            token: Bytes::from_static(SETUP_RESPONSE1_TOKEN),
            client_iv: Bytes::from_static(SETUP_RESPONSE1_CLIENT_IV),
        }
    }

    #[test]
    fn test_setup_response_min_size() {
        assert_eq!(SetupResponse::min_size(), 164);
    }

    #[test]
    fn test_setup_response_parse() {
        let mut buf = BytesMut::from(SETUP_RESPONSE1);
        let expected = get_setup_response();
        let res = SetupResponse::parse(&mut buf);
        assert_eq!(res, Ok(expected))
    }

    #[test]
    fn test_setup_response_size() {
        let sg = get_setup_response();
        assert_eq!(sg.size(), 164)
    }

    #[test]
    fn test_setup_response_write_bytes() {
        let msg = get_setup_response();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(SETUP_RESPONSE1));
    }
}
