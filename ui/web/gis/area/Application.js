//---------------------------------------------------------------------
// gis.area application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.area.Application");

Ext.define("NOC.gis.area.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.gis.area.Model",
    "Ext.ux.form.GeoField",
  ],
  model: "NOC.gis.area.Model",
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },

    {
      text: __("Active"),
      dataIndex: "is_active",
      renderer: NOC.render.Bool,
      width: 50,
    },

    {
      text: __("SW"),
      dataIndex: "SW",
    },

    {
      text: __("NE"),
      dataIndex: "NE",
    },

    {
      text: __("Min. Zoom"),
      dataIndex: "min_zoom",
    },

    {
      text: __("Max. Zoom"),
      dataIndex: "max_zoom",
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
      name: "is_active",
      xtype: "checkboxfield",
      boxLabel: __("Active"),
    },
    {
      name: "SW",
      xtype: "geofield",
      fieldLabel: __("SW"),
      allowBlank: false,
    },
    {
      name: "NE",
      xtype: "geofield",
      fieldLabel: __("NE"),
      allowBlank: false,
    },
    {
      name: "min_zoom",
      xtype: "numberfield",
      fieldLabel: __("Min. Zoom"),
      allowBlank: false,
      defaultValue: 0,
      minValue: 0,
      maxValue: 18,
    },
    {
      name: "max_zoom",
      xtype: "numberfield",
      fieldLabel: __("Max. Zoom"),
      allowBlank: false,
      defaultValue: 18,
      minValue: 0,
      maxValue: 18,
    },
    {
      name: "description",
      xtype: "textfield",
      fieldLabel: __("Description"),
      allowBlank: true,
    },
  ],
});
