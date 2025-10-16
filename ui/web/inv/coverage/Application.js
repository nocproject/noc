//---------------------------------------------------------------------
// inv.coverage application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.coverage.Application");

Ext.define("NOC.inv.coverage.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.inv.coverage.Model",
    "NOC.inv.coverage.BuildingModel",
    "NOC.inv.coverage.ObjectModel",
  ],
  model: "NOC.inv.coverage.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("Description"),
      dataIndex: "description",
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
      name: "description",
      xtype: "textarea",
      fieldLabel: __("Description"),
    },
  ],
  inlines: [
    {
      title: __("Covered Buildings"),
      model: "NOC.inv.coverage.BuildingModel",
      columns: [
        {
          text: __("Pref."),
          tooltip: __("Preference"),
          dataIndex: "preference",
          width: 50,
          textAlign: "right",
        },
        {
          text: __("Building"),
          dataIndex: "building",
          renderer: NOC.render.Lookup("building"),
          flex: 1,
        },
        {
          text: __("Entrance"),
          dataIndex: "entrance",
          width: 100,
        },
      ],
    },
    {
      title: __("Covered Objects"),
      model: "NOC.inv.coverage.ObjectModel",
      columns: [
        {
          text: __("Pref."),
          tooltip: __("Preference"),
          dataIndex: "preference",
          width: 50,
          textAlign: "right",
        },
        {
          text: __("Object"),
          dataIndex: "object",
          renderer: NOC.render.Lookup("object"),
          flex: 1,
        },
      ],
    },
  ],
});
