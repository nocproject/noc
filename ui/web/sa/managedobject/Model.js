//---------------------------------------------------------------------
// sa.managedobject Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.Model");

Ext.define("NOC.sa.managedobject.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/managedobject/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "is_managed",
      type: "boolean",
      persist: false,
      defaultValue: true,
    },
    {
      name: "administrative_domain",
      type: "int",
      defaultValue: 1,
    },
    {
      name: "administrative_domain__label",
      type: "string",
      persist: false,
    },
    {
      name: "auth_profile",
      type: "int",
      defaultValue: null,
    },
    {
      name: "auth_profile__label",
      type: "string",
      persist: false,
    },
    {
      name: "pool",
      type: "string",
    },
    {
      name: "pool__label",
      type: "string",
      persist: false,
    },
    {
      name: "fm_pool",
      type: "string",
    },
    {
      name: "fm_pool__label",
      type: "string",
      persist: false,
    },
    {
      name: "segment",
      type: "string",
    },
    {
      name: "segment__label",
      type: "string",
      persist: false,
    },
    {
      name: "project",
      type: "string",
    },
    {
      name: "project__label",
      type: "string",
      persist: false,
    },
    {
      name: "profile",
      type: "string",
    },
    {
      name: "profile__label",
      type: "string",
      persist: false,
    },
    {
      name: "vendor",
      type: "string",
      defaultValue: null,
    },
    {
      name: "vendor__label",
      type: "string",
      persist: false,
    },
    {
      name: "platform",
      type: "string",
      defaultValue: null,
    },
    {
      name: "platform__label",
      type: "string",
      persist: false,
    },
    {
      name: "version",
      type: "string",
      defaultValue: null,
    },
    {
      name: "version__label",
      type: "string",
      persist: false,
    },
    {
      name: "next_version",
      type: "string",
    },
    {
      name: "next_version__label",
      type: "string",
      persist: false,
    },
    {
      name: "software_image",
      type: "string",
    },
    {
      name: "object_profile",
      type: "int",
      defaultValue: 1,
    },
    {
      name: "object_profile__label",
      type: "string",
      persist: false,
    },
    {
      name: "description",
      type: "string",
      defaultValue: "",
    },
    {
      name: "scheme",
      type: "int",
      defaultValue: 1,
    },
    {
      name: "address",
      type: "string",
    },
    {
      name: "port",
      type: "int",
      defaultValue: 0,
    },
    {
      name: "user",
      type: "string",
      defaultValue: null,
    },
    {
      name: "password",
      type: "string",
      defaultValue: null,
    },
    {
      name: "super_password",
      type: "string",
      defaultValue: null,
    },
    {
      name: "remote_path",
      type: "string",
    },
    {
      name: "trap_source_ip",
      type: "string",
    },
    {
      name: "syslog_source_ip",
      type: "string",
    },
    {
      name: "trap_source_type",
      type: "string",
      defaultValue: "m",
    },
    {
      name: "syslog_source_type",
      type: "string",
      defaultValue: "m",
    },
    {
      name: "trap_community",
      type: "string",
    },
    {
      name: "snmp_ro",
      type: "string",
      defaultValue: null,
    },
    {
      name: "snmp_rw",
      type: "string",
      defaultValue: null,
    },
    {
      name: "snmp_rate_limit",
      type: "int",
      defaultValue: 0,
    },
    {
      name: "l2_domain",
      type: "string",
    },
    {
      name: "l2_domain__label",
      type: "string",
      persist: false,
    },
    {
      name: "vrf",
      type: "int",
    },
    {
      name: "vrf__label",
      type: "string",
      persist: false,
    },
    {
      name: "shape",
      type: "string",
    },
    {
      name: "shape_overlay_glyph",
      type: "string",
    },
    {
      name: "shape_overlay_glyph__label",
      type: "string",
      persist: false,
    },
    {
      name: "shape_overlay_position",
      type: "string",
    },
    {
      name: "shape_overlay_form",
      type: "string",
    },
    {
      name: "shape_title_template",
      type: "string",
    },
    {
      name: "config_filter_handler",
      type: "string",
    },
    {
      name: "config_filter_handler__label",
      type: "string",
      persist: false,
    },
    {
      name: "config_diff_filter_handler",
      type: "string",
    },
    {
      name: "config_diff_filter_handler__label",
      type: "string",
      persist: false,
    },
    {
      name: "config_validation_handler",
      type: "string",
    },
    {
      name: "config_validation_handler__label",
      type: "string",
      persist: false,
    },
    {
      name: "max_scripts",
      type: "int",
      defaultValue: 0,
    },
    {
      name: "time_pattern",
      type: "string",
    },
    {
      name: "time_pattern__label",
      type: "string",
      persist: false,
    },
    {
      name: "controller",
      type: "string",
      defaultValue: null,
    },
    {
      name: "controller__label",
      type: "string",
      persist: false,
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "interface_count",
      type: "int",
      persist: false,
    },
    {
      name: "oper_state",
      type: "string",
      persist: false,
    },
    {
      name: "oper_state__label",
      type: "string",
      persist: false,
    },
    {
      name: "link_count",
      type: "int",
      persist: false,
    },
    {
      name: "remote_system",
      type: "string",
      defaultValue: null,
    },
    {
      name: "remote_system__label",
      type: "string",
      persist: false,
    },
    {
      name: "remote_id",
      type: "string",
    },
    {
      name: "bi_id",
      type: "string",
    },
    {
      name: "autosegmentation_policy",
      type: "string",
      defaultValue: "p",
    },
    {
      name: "tt_system",
      type: "string",
      defaultValue: null,
    },
    {
      name: "tt_system__label",
      type: "string",
      persist: false,
    },
    {
      name: "tt_queue",
      type: "string",
    },
    {
      name: "tt_system_id",
      type: "string",
    },
    {
      name: "escalation_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "syslog_archive_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "box_discovery_alarm_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "periodic_discovery_alarm_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "box_discovery_running_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "periodic_discovery_running_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "cli_session_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "cli_privilege_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "access_preference",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "box_discovery_telemetry_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "box_discovery_telemetry_sample",
      type: "int",
      defaultValue: 0,
    },
    {
      name: "periodic_discovery_telemetry_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "periodic_discovery_telemetry_sample",
      type: "int",
      defaultValue: 0,
    },
    {
      name: "event_processing_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "address_resolution_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "denied_firmware_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "fqdn",
      type: "string",
    },
    {
      name: "config_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "config_fetch_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "interface_discovery_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "caps_discovery_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "vlan_discovery_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "confdb_raw_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "dynamic_classification_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "static_service_groups",
      type: "auto",
    },
    {
      name: "effective_service_groups",
      type: "auto",
      persist: false,
    },
    {
      name: "static_client_groups",
      type: "auto",
    },
    {
      name: "effective_client_groups",
      type: "auto",
      persist: false,
    },
    {
      name: "effective_labels",
      type: "auto",
      persist: false,
    },
    {
      name: "state",
      type: "string",
    },
    {
      name: "state__label",
      type: "string",
      persist: false,
    },
    {
      name: "diagnostics",
      type: "auto",
      persist: false,
    },
    {
      name: "row_class",
      type: "string",
      persist: false,
    },
    {
      name: "snmp_security_level",
      type: "string",
    },
    {
      name: "snmp_username",
      type: "string",
    },
    {
      name: "snmp_ctx_name",
      type: "string",
    },
    {
      name: "snmp_auth_proto",
      type: "string",
    },
    {
      name: "snmp_auth_key",
      type: "string",
    },
    {
      name: "snmp_priv_proto",
      type: "string",
    },
    {
      name: "snmp_priv_key",
      type: "string",
    },
  ],
});
