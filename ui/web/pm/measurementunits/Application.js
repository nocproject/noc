//---------------------------------------------------------------------
// pm.measurementunits application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.measurementunits.Application");

Ext.define("NOC.pm.measurementunits.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.pm.measurementunits.Model",
    "Ext.ux.form.ColorField",
    "NOC.pm.measurementunits.LookupField"],
  model: "NOC.pm.measurementunits.Model",
  search: true,

  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/pm/measurementunits/{0}/json/",
      previewName: "Scope: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 100,
        },
        {
          text: __("Code"),
          dataIndex: "code",
          width: 100,
        },
        {
          text: __("Base"),
          dataIndex: "base_unit",
          renderer: NOC.render.Lookup("base_unit"),
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
          uiStyle: "medium",
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
          allowBlank: true,
        },
        {
          name: "base_unit",
          xtype: "pm.measurementunits.LookupField",
          fieldLabel: __("Base Measurement Units"),
          allowBlank: true,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
          uiStyle: "extra",
        },
        {
          name: "code",
          xtype: "textfield",
          fieldLabel: __("Code"),
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "label",
          xtype: "textfield",
          fieldLabel: __("Label"),
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "dashboard_label",
          xtype: "textfield",
          fieldLabel: __("Dashboard Label"),
          uiStyle: "medium",
        },
        {
          name: "dashboard_sr_color",
          xtype: "colorfield",
          fieldLabel: __("Dashboard Series Color"),
          allowBlank: true,
          uiStyle: "medium",
        },
        {
          name: "convert_from",
          xtype: "gridfield",
          fieldLabel: __("Convert form for BaseUnit"),
          allowBlank: true,
          columns: [
            {
              text: __("Measurment Unit"),
              dataIndex: "unit",
              width: 200,
              editor: {
                xtype: "pm.measurementunits.LookupField",
              },
              renderer: NOC.render.Lookup("unit"),
            },
            {
              text: __("Expresseion"),
              dataIndex: "expr",
              flex: 1,
              editor: "textfield",
            },
          ],
        },
        {
          name: "enum",
          xtype: "gridfield",
          fieldLabel: __("Enumeration"),
          allowBlank: true,
          columns: [
            {
              text: __("Key"),
              dataIndex: "key",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Value"),
              dataIndex: "value",
              flex: 1,
              editor: "numberfield",
            },
          ],
        },
      ],
      formToolbar: [
        {
          text: __("JSON"),
          glyph: NOC.glyph.file,
          tooltip: __("Show JSON"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onJSON,
        },
      ],
    });
    me.callParent();
  },
  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
