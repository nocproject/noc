// ---------------------------------------------------------------------
// PacketModel benchmarks
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use agent::proto::pktmodel::{PacketModels,ModelConfig,GetPacket,G711ModelConfig,G729ModelConfig,CbrModelConfig,ImixModelConfig};
use criterion::{criterion_group, criterion_main, Criterion};
use std::convert::TryFrom;

fn pktmodel_benchmark(c: &mut Criterion) {
    c.bench_function("g711_get_packet", |b| {
        let model = PacketModels::try_from(ModelConfig::G711(G711ModelConfig {})).unwrap();
        b.iter(|| model.get_packet(0));
    });
    c.bench_function("g729_get_packet", |b| {
        let model = PacketModels::try_from(ModelConfig::G729(G729ModelConfig {})).unwrap();
        b.iter(|| model.get_packet(0));
    });
    c.bench_function("cbr_get_packet", |b| {
        let model = PacketModels::try_from(ModelConfig::Cbr(CbrModelConfig {
            bandwidth: 10_000_000,
            size: 100,
        })).unwrap();
        b.iter(|| model.get_packet(0));
    });
    c.bench_function("imix_get_packet", |b| {
        let model = PacketModels::try_from(ModelConfig::Imix(ImixModelConfig {
            bandwidth: 10_000_000,
        })).unwrap();
        b.iter(|| model.get_packet(0));
    });
}

criterion_group!(benches, pktmodel_benchmark);
criterion_main!(benches);
