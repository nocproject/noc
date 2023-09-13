# Compilation Features

`noc-agent` can be configured during compile time by setting or disabling
the `features`

## Config Discovery

Config discovery process is responsible for detection of config file location.
At least one feature must be selected.

| Feature         | Default   | Description                                         |
| --------------- | --------- | --------------------------------------------------- |
| `config-static` | {{ yes }} | Config path are set via command line arguments      |
| `config-zk`     | {{ yes }} | Config location is determined via ZeroConf protocol |

## Config Reader

Config reader is responsible for fetching configuration file.
At least one feature must be selected.

| Feature       | Default   | Description                          |
| ------------- | --------- | ------------------------------------ |
| `config-file` | {{ yes }} | Read config as file from file system |

## Config Format

Config may be encoded in different formats. At least one feature must be selected.

| Feature       | Default   | Description        |
| ------------- | --------- | ------------------ |
| `config-json` | {{ yes }} | JSON config format |
| `config-yaml` | {{ yes }} | YAML config format |

## Collectors

Collectors are responsible for running probes and collecting metrics.
Disabled probes are ignored.

| Feature           | Default   | Description                                        |
| ----------------- | --------- | -------------------------------------------------- |
| `block-io`        | {{ yes }} | [`block_io`](collectors/block_io.md)               |
| `cpu`             | {{ yes }} | [`cpu`](collectors/cpu.md)                         |
| `dns`             | {{ yes }} | [`dns`](collectors/dns.md)                         |
| `fs`              | {{ yes }} | [`fs`](collectors/fs.md)                           |
| `memory`          | {{ yes }} | [`memory`](collectors/memory.md)                   |
| `modbus_rtu`      | {{ yes }} | [`modbus_rtu`](collectors/modbus_rtu.md)           |
| `modbus_tcp`      | {{ yes }} | [`modbus_tcp`](collectors/modbus_tcp.md)           |
| `network`         | {{ yes }} | [`network`](collectors/network.md)                 |
| `test`            | {{ yes }} | [`test`](collectors/test.md)                       |
| `twamp-sender`    | {{ yes }} | [`twamp_sender`](collectors/twamp_sender.md)       |
| `twamp-reflector` | {{ yes }} | [`twamp_reflector`](collectors/twamp_reflector.md) |
| `uptime`          | {{ yes }} | [`uptime`](collectors/uptime.md)                   |
