//---------------------------------------------------------------------
// sa.service Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.Model");

Ext.define("NOC.sa.service.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/service/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "cpe_serial",
      type: "string",
    },
    {
      name: "name_template",
      type: "string",
    },
    {
      name: "state",
      type: "string",
    },
    {
      name: "ts",
      type: "auto",
    },
    {
      name: "cpe_group",
      type: "string",
    },
    {
      name: "bi_id",
      type: "string",
      persist: false,
    },
    {
      name: "cpe_model",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "cpe_mac",
      type: "string",
    },
    {
      name: "remote_id",
      type: "string",
    },
    {
      name: "subscriber",
      type: "string",
    },
    {
      name: "subscriber__label",
      type: "string",
      persist: false,
    },
    {
      name: "supplier",
      type: "string",
    },
    {
      name: "supplier__label",
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
      name: "stage_name",
      type: "string",
    },
    {
      name: "account_id",
      type: "string",
    },
    {
      name: "parent",
      type: "string",
    },
    {
      name: "label",
      type: "string",
      persist: false,
    },
    {
      name: "order_id",
      type: "string",
    },
    {
      name: "nri_port",
      type: "string",
    },
    {
      name: "address",
      type: "string",
    },
    {
      name: "agreement_id",
      type: "string",
    },
    {
      name: "stage_id",
      type: "string",
    },
    {
      name: "state_changed",
      type: "auto",
    },
    {
      name: "remote_system",
      type: "string",
    },
    {
      name: "remote_system__label",
      type: "string",
      persist: false,
    },
    {
      name: "stage_start",
      type: "auto",
    },
    {
      name: "caps",
      type: "auto",
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
      name: "oper_status",
      type: "string",
      persist: false,
    },
    {
      name: "static_instances",
      type: "auto",
    },
    {
      name: "status_transfer_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "status_dependencies",
      type: "auto",
    },
    {
      name: "calculate_status_function",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "calculate_status_rules",
      type: "auto",
    },
    {
      name: "labels",
      type: "auto",
    },
  ],
});
