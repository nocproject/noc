// ---------------------------------------------------------------------
// PacketModel benchmarks
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use agent::proto::pktmodel::ModelConfig;
use criterion::{criterion_group, criterion_main, Criterion};

fn pktmodel_benchmark(c: &mut Criterion) {
    c.bench_function("g711_get_packet", |b| {
        let get_packet = ModelConfig::G711 {}.get_model();
        b.iter(|| get_packet(0));
    });
    c.bench_function("g729_get_packet", |b| {
        let get_packet = ModelConfig::G729 {}.get_model();
        b.iter(|| get_packet(0));
    });
    c.bench_function("cbr_get_packet", |b| {
        let get_packet = ModelConfig::Cbr {
            bandwidth: 10_000_000,
            size: 100,
        }
        .get_model();
        b.iter(|| get_packet(0));
    });
    c.bench_function("imix_get_packet", |b| {
        let get_packet = ModelConfig::Imix {
            bandwidth: 10_000_000,
        }
        .get_model();
        b.iter(|| get_packet(0));
    });
}

criterion_group!(benches, pktmodel_benchmark);
criterion_main!(benches);
