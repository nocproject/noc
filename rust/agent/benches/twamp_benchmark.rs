// ---------------------------------------------------------------------
// TWAMP benchmarks
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use agent::proto::frame::{FrameReader, FrameWriter};
use agent::proto::twamp::{NTPTimeStamp, TestRequest, TestResponse, UTCDateTime};
use bytes::BytesMut;
use chrono::{TimeZone, Utc};
use criterion::{criterion_group, criterion_main, Criterion};

#[inline]
fn utc_now() {
    Utc::now();
}

#[inline]
fn ntp_timestamp_new(secs: u32, fracs: u32) {
    NTPTimeStamp::new(secs, fracs);
}

#[inline]
fn ntp_to_utc(ntp_ts: NTPTimeStamp) {
    let _: UTCDateTime = ntp_ts.into();
}

#[inline]
fn utc_to_ntp(utc_ts: UTCDateTime) {
    let _: NTPTimeStamp = utc_ts.into();
}

static TEST_REQUEST: &[u8] = &[
    0x00, 0x00, 0x04, 0x00, // Sequence, 4 octets
    0xe3, 0xd0, 0xd0, 0x20, 0x00, 0x00, 0x00, 0x00, // Timestamp, 8 octets
    0x00, 0x0f, // Err estimate, 2 octets
];

#[inline]
fn parse_test_request() {
    let mut buf = BytesMut::from(TEST_REQUEST);
    let _ = TestRequest::parse(&mut buf);
}

#[inline]
fn write_test_request(req: &TestRequest, buf: &mut BytesMut) {
    buf.clear();
    req.write_bytes(buf);
}

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
];

#[inline]
fn parse_test_response() {
    let mut buf = BytesMut::from(TEST_RESPONSE);
    let _ = TestResponse::parse(&mut buf);
}

fn twamp_benchmark(c: &mut Criterion) {
    c.bench_function("utc_now", |b| b.iter(|| utc_now()));
    c.bench_function("ntp_timestamp_new", |b| {
        b.iter(|| ntp_timestamp_new(3822112800, 2147483647))
    });
    c.bench_function("ntp_to_utc", |b| {
        let ts = NTPTimeStamp::new(3822112800, 2147483647);
        b.iter(|| ntp_to_utc(ts))
    });
    c.bench_function("utc_to_ntp", |b| {
        let ts = Utc.ymd(2021, 2, 12).and_hms_milli(10, 0, 0, 500);
        b.iter(|| utc_to_ntp(ts))
    });
    c.bench_function("parse_test_request", |b| b.iter(|| parse_test_request()));
    c.bench_function("write_test_request", |b| {
        let req = TestRequest {
            seq: 1024,
            timestamp: Utc.ymd(2021, 2, 12).and_hms(10, 0, 0),
            err_estimate: 15,
            pad_to: 20,
        };
        let mut buf = BytesMut::with_capacity(req.size());
        b.iter(|| write_test_request(&req, &mut buf))
    });
    c.bench_function("parse_test_response", |b| b.iter(|| parse_test_response()));
}

criterion_group!(benches, twamp_benchmark);
criterion_main!(benches);
