use byteorder::{BigEndian, ByteOrder};
use internet_checksum::checksum;
use pyo3::{prelude::*, types::PyBytes};

// Module initialization
#[pymodule]
fn ip(_py: Python, m: &PyModule) -> PyResult<()> {
    /// Build ICMP echo request packet
    /// ```text
    ///  0                   1                   2                   3
    ///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    /// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    /// | Type          | Code          | Checksum                      |
    /// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    /// | Request Id                    | Sequence                      |
    /// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    /// Where:
    /// * `type` - 8, echo request
    /// * `code` - 0
    /// ```
    #[pyfn(m)]
    fn build_icmp_echo_request<'a>(
        py: Python<'a>,
        request_id: u16,
        seq: u16,
        payload: &'a [u8],
    ) -> PyResult<&'a PyBytes> {
        PyBytes::new_with(py, 8 + payload.len(), |buf: &mut [u8]| {
            // Type = 8, Code = 0, Checksum filler = 9
            BigEndian::write_u32(buf, 0x08000000);
            // Request id, 2 octets
            BigEndian::write_u16(&mut buf[4..], request_id);
            // Sequence, 2 octets
            BigEndian::write_u16(&mut buf[6..], seq);
            // Clone payload
            buf[8..].copy_from_slice(payload);
            // Calculate checksum
            // RFC-1071
            let cs = checksum(buf);
            buf[2] = cs[0];
            buf[3] = cs[1];
            Ok(())
        })
    }
    /// Build ICMP echo request packet with timestamp information
    /// ```text
    ///  0                   1                   2                   3
    ///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    /// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    /// | Type          | Code          | Checksum                      |
    /// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    /// | Request Id                    | Sequence                      |
    /// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    /// | Timestamp                                                     |
    /// |                                                               |
    /// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    /// Where:
    /// * `type` - 8, echo request
    /// * `code` - 0
    /// ```
    #[pyfn(m)]
    fn build_icmp_echo_request_ts(
        py: Python,
        request_id: u16,
        seq: u16,
        ts: u64,
        payload_len: usize,
    ) -> PyResult<&PyBytes> {
        PyBytes::new_with(py, 8 + payload_len, |buf: &mut [u8]| {
            // Type = 8, Code = 0, Checksum filler = 9
            BigEndian::write_u32(buf, 0x08000000);
            // Request id, 2 octets
            BigEndian::write_u16(&mut buf[4..], request_id);
            // Sequence, 2 octets
            BigEndian::write_u16(&mut buf[6..], seq);
            // Timestamp, 8 octets
            BigEndian::write_u64(&mut buf[8..], ts);
            // Generate padding
            buf[16..].fill(48u8);
            // Calculate checksum
            // RFC-1071
            let cs = checksum(buf);
            buf[2] = cs[0];
            buf[3] = cs[1];
            Ok(())
        })
    }
    // Module is ok
    Ok(())
}
