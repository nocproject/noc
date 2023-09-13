# Config Diff Filter Handler


Interface for configuration comparison filter. Config diff filters
are applied both to last and current config to avoid misdetection
of configuration changes due to constantly changing parts.
Results of Config Diff Filter don't stored in GridVCS and used for
comparison only.

Config filters are applied after [Config Filter](config-filter.md).

    config_diff_filter(managed_object, config):
        Implements config diff filter
    
        :param managed_object: Managed Object instance
        :param config: Config
        :returns: altered config

## Examples


### Hide altering part

Remove *ntp date XXX*

    import re

    rx_ntp = re.compile("^ntp\s+date\s+\d+$", re.MULTILINE)

    def config_diff_filter(mo, config):
        return rx_ntp.sub("", rx_password)
