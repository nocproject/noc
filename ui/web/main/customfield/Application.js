//---------------------------------------------------------------------
// main.customfield application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.customfield.Application");

Ext.define("NOC.main.customfield.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.customfield.Model",
    "NOC.main.ref.modcol.LookupField",
    "NOC.main.customfieldenumgroup.LookupField",
  ],
  model: "NOC.main.customfield.Model",
  search: true,
  columns: [
    {
      text: __("Table"),
      dataIndex: "table",
    },
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("Active"),
      dataIndex: "is_active",
      renderer: NOC.render.Bool,
    },
    {
      text: __("Label"),
      dataIndex: "label",
    },
    {
      text: __("Type"),
      dataIndex: "type",
    },
    {
      text: __("Enum Group"),
      dataIndex: "enum_group",
      renderer: NOC.render.Lookup("enum_group"),
    },
    {
      text: __("Indexed"),
      dataIndex: "is_indexed",
      renderer: NOC.render.Bool,
    },
    {
      text: __("Searchable"),
      dataIndex: "is_searchable",
      renderer: NOC.render.Bool,
    },
    {
      text: __("Filtered"),
      dataIndex: "is_filtered",
      renderer: NOC.render.Bool,
    },
    {
      text: __("Hidden"),
      dataIndex: "is_hidden",
      renderer: NOC.render.Bool,
    },
  ],
  fields: [
    {
      name: "table",
      xtype: "main.ref.modcol.LookupField",
      fieldLabel: __("Table"),
      allowBlank: false,
    },
    {
      name: "name",
      xtype: "textfield",
      fieldLabel: __("Name"),
      allowBlank: false,
      regex: /^[a-zA-Z0-9_]+$/,
    },
    {
      name: "is_active",
      xtype: "checkboxfield",
      boxLabel: __("Is Active"),
      allowBlank: false,
    },
    {
      name: "label",
      xtype: "textfield",
      fieldLabel: __("Label"),
      allowBlank: false,
    },
    {
      name: "type",
      xtype: "combobox",
      fieldLabel: __("Type"),
      allowBlank: false,
      queryMode: "local",
      displayField: "label",
      valueField: "id",
      store: {
        fields: ["id", "label"],
        data: [
          {id: "str", label: "String"},
          {id: "int", label: "Integer"},
          {id: "bool", label: "Boolean"},
          {id: "date", label: "Date"},
          {id: "datetime", label: "Date&Time"},
        ],
      },
    },
    {
      name: "enum_group",
      xtype: "main.customfieldenumgroup.LookupField",
      fieldLabel: __("Enum Group"),
      allowBlank: true,
      query: {
        is_active: true,
      },
    },
    {
      name: "description",
      xtype: "textarea",
      fieldLabel: __("Description"),
      allowBlank: true,
    },
    {
      name: "max_length",
      xtype: "numberfield",
      fieldLabel: __("Max. Length"),
      allowBlank: true,
    },
    {
      name: "regexp",
      xtype: "textfield",
      fieldLabel: __("Regexp"),
      allowBlank: true,
    },
    {
      name: "is_indexed",
      xtype: "checkboxfield",
      boxLabel: __("Is Indexed"),
      allowBlank: false,
    },
    {
      name: "is_searchable",
      xtype: "checkboxfield",
      boxLabel: __("Is Searchable"),
      allowBlank: false,
    },
    {
      name: "is_filtered",
      xtype: "checkboxfield",
      boxLabel: __("Is Filtered"),
      allowBlank: false,
    },
    {
      name: "is_hidden",
      xtype: "checkboxfield",
      boxLabel: __("Is Hidden"),
      allowBlank: false,
    },
  ],
  filters: [
    {
      title: __("By Active"),
      name: "is_active",
      ftype: "boolean",
    },
    {
      title: __("By Searchable"),
      name: "is_searchable",
      ftype: "boolean",
    },
    {
      title: __("By Filtered"),
      name: "is_filtered",
      ftype: "boolean",
    },
    {
      title: __("By Hidden"),
      name: "is_hidden",
      ftype: "boolean",
    },
  ],
});
