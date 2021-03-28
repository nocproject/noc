// ---------------------------------------------------------------------
// TWAMP Test-Response structure
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{NtpTimeStamp, UtcDateTime};
use crate::proto::frame::{FrameError, FrameReader, FrameWriter};
use bytes::{Buf, BufMut, BytesMut};

/// ## Test-Response structure
/// RFC-5357: 4.2.1
/// NB: Unauthorized mode only
/// ```text
/// 0                   1                   2                   3
/// 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                        Sequence Number                        |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                          Timestamp                            |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |         Error Estimate        |           MBZ                 |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                          Receive Timestamp                    |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                        Sender Sequence Number                 |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                      Sender Timestamp                         |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |      Sender Error Estimate    |           MBZ                 |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |  Sender TTL   |                                               |
/// +-+-+-+-+-+-+-+-+                                               +
/// |                                                               |
/// .                                                               .
/// .                         Packet Padding                        .
/// .                                                               .
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// ```
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct TestResponse {
    pub seq: u32,
    pub timestamp: UtcDateTime,
    pub err_estimate: u16,
    pub recv_timestamp: UtcDateTime,
    pub sender_seq: u32,
    pub sender_timestamp: UtcDateTime,
    pub sender_err_estimate: u16,
    pub sender_ttl: u8,
    // Padding to size, excluding IP + UDP
    pub pad_to: usize,
}

impl FrameReader for TestResponse {
    fn min_size() -> usize {
        41
    }
    fn parse(s: &mut BytesMut) -> Result<TestResponse, FrameError> {
        let pad_to = s.len();
        // Sequence number, 4 octets
        let seq = s.get_u32();
        // Timestamp, 8 octets
        let ts = NtpTimeStamp::new(s.get_u32(), s.get_u32());
        // Err estimate, 2 octets
        let err_estimate = s.get_u16();
        // MBZ, 2 octets
        s.advance(2);
        // Receive timestamp, 8 octets
        let recv_ts = NtpTimeStamp::new(s.get_u32(), s.get_u32());
        // Sender sequence number, 4 octets
        let sender_seq = s.get_u32();
        // Sender timestamp
        let sender_ts = NtpTimeStamp::new(s.get_u32(), s.get_u32());
        // Sender err estimate, 2 octets
        let sender_err_estimate = s.get_u16();
        // MBZ, 2 octets
        s.advance(2);
        // Sender TTL, 1 octet
        let sender_ttl = s.get_u8();
        // Skip padding
        if 41 < pad_to {
            s.advance(pad_to - 41)
        }
        Ok(TestResponse {
            seq,
            timestamp: ts.into(),
            err_estimate,
            recv_timestamp: recv_ts.into(),
            sender_seq,
            sender_timestamp: sender_ts.into(),
            sender_err_estimate,
            sender_ttl,
            pad_to,
        })
    }
}

impl FrameWriter for TestResponse {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        self.pad_to
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), FrameError> {
        // Sequence number, 4 octets
        s.put_u32(self.seq);
        // Timestamp, 8 octets
        let ts: NtpTimeStamp = self.timestamp.into();
        s.put_u32(ts.secs());
        s.put_u32(ts.fracs());
        // Err estimate, 2 octets
        s.put_u16(self.err_estimate);
        // MBZ, 2 octets
        s.put_u16(0);
        // Receive timestamp, 8 octets
        let ts: NtpTimeStamp = self.recv_timestamp.into();
        s.put_u32(ts.secs());
        s.put_u32(ts.fracs());
        // Sender sequence number, 4 octets
        s.put_u32(self.sender_seq);
        // Sender timestamp
        let ts: NtpTimeStamp = self.sender_timestamp.into();
        s.put_u32(ts.secs());
        s.put_u32(ts.fracs());
        // Sender err estimate, 2 octets
        s.put_u16(self.sender_err_estimate);
        // MBZ, 2 octets
        s.put_u16(0);
        // Sender TTL, 1 octet
        s.put_u8(self.sender_ttl);
        // Add padding
        const MIN_LEN: usize = 41;
        if self.pad_to > MIN_LEN {
            s.resize(self.pad_to, 0);
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::TestResponse;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use bytes::{Buf, BytesMut};
    use chrono::{TimeZone, Utc};

    static TEST_RESPONSE: &[u8] = &[
        0x00, 0x00, 0x04, 0x00, // Sequence, 4 octets
        0xe3, 0xd0, 0xd0, 0x22, 0x00, 0x00, 0x00, 0x00, // Timestamp, 8 octets
        0x00, 0x0f, // Err estimate, 2 octets
        0x00, 0x00, // MBZ, 2 octets
        0xe3, 0xd0, 0xd0, 0x21, 0x00, 0x00, 0x00, 0x00, // Receive timestamp, 8 octets
        0x00, 0x00, 0x04, 0x01, // Sender Sequence, 4 octets
        0xe3, 0xd0, 0xd0, 0x20, 0x00, 0x00, 0x00, 0x00, // Sender Timestamp, 8 octets
        0x00, 0x0e, // Sender Err estimate, 2 octets
        0x00, 0x00, // MBZ, 2 octets
        0xfa, // Sender TTL
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // Padding, 9 octets
    ];

    fn get_test_response() -> TestResponse {
        TestResponse {
            seq: 1024,
            timestamp: Utc.ymd(2021, 2, 12).and_hms(10, 0, 2),
            err_estimate: 15,
            recv_timestamp: Utc.ymd(2021, 2, 12).and_hms(10, 0, 1),
            sender_seq: 1025,
            sender_timestamp: Utc.ymd(2021, 2, 12).and_hms(10, 0, 0),
            sender_err_estimate: 14,
            sender_ttl: 250,
            pad_to: 50,
        }
    }

    #[test]
    fn test_test_response_min_size() {
        assert_eq!(TestResponse::min_size(), 41);
    }

    #[test]
    fn test_test_response_parse() {
        let mut buf = BytesMut::from(TEST_RESPONSE);
        let expected = get_test_response();
        let res = TestResponse::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert_eq!(res, Ok(expected))
    }

    #[test]
    fn test_test_response_size() {
        let sg = get_test_response();
        assert_eq!(sg.size(), 50)
    }

    #[test]
    fn test_test_response_write_bytes() {
        let msg = get_test_response();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(TEST_RESPONSE));
    }
}
