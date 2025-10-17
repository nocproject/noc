//---------------------------------------------------------------------
// vc.vlanfilter application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlanfilter.Application");

Ext.define("NOC.vc.vlanfilter.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.vc.vlanfilter.Model",
    "Ext.ux.form.GridField",
    "NOC.core.label.LabelField",
  ],
  model: "NOC.vc.vlanfilter.Model",
  search: true,
  helpId: "reference-vlanfilter-filter",

  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("Include Expression"),
      dataIndex: "include_expression",
      flex: 1,
    },
    {
      text: __("Exclude Expression"),
      dataIndex: "exclude_expression",
      flex: 1,
    },
  ],
  fields: [
    {
      name: "name",
      xtype: "textfield",
      fieldLabel: __("Name"),
      allowBlank: false,
    },
    {
      name: "include_expression",
      xtype: "textfield",
      fieldLabel: __("Include Expression"),
      allowBlank: false,
      regex: /^\s*\d+\s*(-\d+\s*)?(,\s*\d+\s*(-\d+)?)*$/,
    },
    {
      name: "exclude_expression",
      xtype: "textfield",
      fieldLabel: __("Exclude Expression"),
      allowBlank: true,
      regex: /^\s*\d+\s*(-\d+\s*)?(,\s*\d+\s*(-\d+)?)*$/,
    },
    {
      name: "description",
      xtype: "textarea",
      fieldLabel: __("Description"),
      allowBlank: true,
    },
    {
      name: "match_labels",
      xtype: "gridfield",
      fieldLabel: __("Match Labels"),
      disabled: true,
      columns: [
        {
          text: __("Labels"),
          dataIndex: "labels",
          renderer: NOC.render.LabelField,
          editor: {
            xtype: "labelfield",
          },
          width: 200,
        },
        {
          dataIndex: "scope",
          text: __("Scope"),
          editor: "textfield",
          width: 150,
        },
      ],
    },
  ],
  filters: [
    {
      title: __("By VLAN"),
      name: "include_expression",
      ftype: "vc",
    },
  ],
});
