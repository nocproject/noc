# ConfDB tokenizer and normalizer tests
Test are processed by tests/confdb/test_profiles.py runner.

## Run manually
```
$ pytest -vv tests/confdb/test_profiles.py
```

## Tests directory tree
Each test is separate YAML file with `.yml` extension.
Files are groupped into directories according to profile.
i.e. `Juniper.JUNOS` tests must be inside `tests/confdb/profiles/Juniper/JUNOS`
directory.

## Test structure
Each test must have `config` and `result` section at least:

```
config: |
  system {
    name-server [ "ns1.example.com" "ns2.example.com" ];
    domain-search [ "test.example.com" "example.com" ];
  }
result:
  - ["protocols", "dns", "name-server", "ns1.example.com"]
  - ["protocols", "dns", "name-server", "ns2.example.com"]
  - ["protocols", "dns", "search", "test.example.com"]
  - ["protocols", "dns", "search", "example.com"]
```

YAML file must have two-space identation. Pipe (`|`) construction should
be used for multi-line configs.
