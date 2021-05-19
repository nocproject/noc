//---------------------------------------------------------------------
// pm.measurementunits application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.measurementunits.Application");

Ext.define("NOC.pm.measurementunits.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.pm.measurementunits.Model", "Ext.ux.form.ColorField"],
  model: "NOC.pm.measurementunits.Model",
  search: true,

  initComponent: function() {
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: new Ext.XTemplate("/pm/measurementunits/{id}/json/"),
      previewName: new Ext.XTemplate("Scope: {name}")
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: "Name",
          dataIndex: "name",
          flex: 1
        }
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "medium"
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
          allowBlank: true
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
          uiStyle: "extra"
        },
        {
          name: "label",
          xtype: "textfield",
          fieldLabel: __("Label"),
          allowBlank: false,
          uiStyle: "medium"
        },
        {
          name: "dashboard_label",
          xtype: "textfield",
          fieldLabel: __("Dashboard Label"),
          uiStyle: "medium"
        },
        {
          name: "dashboard_sr_color",
          xtype: "colorfield",
          fieldLabel: __("Dashboard Series Color"),
          allowBlank: true,
          uiStyle: "medium"
        },
        {
          name: "scale_type",
          xtype: "combobox",
          fieldLabel: __("Scale Type"),
          allowBlank: false,
          uiStyle: "medium",
          store: [["d", __("Decimal Scale")], ["b", __("Binary Scale")]]
        },
        {
          name: "alt_units",
          xtype: "gridfield",
          fieldLabel: __("Alternative Units"),
          allowBlank: true,
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 100,
              editor: "textfield"
            },
            {
              text: __("Description"),
              dataIndex: "description",
              width: 250,
              editor: "textfield"
            },
            {
              text: __("Label"),
              dataIndex: "label",
              width: 75,
              editor: "textfield"
            },
            {
              text: __("Dash. Label"),
              dataIndex: "dashboard_label",
              width: 75,
              editor: "textfield"
            },
            {
              text: __("From Primary"),
              dataIndex: "from_primary",
              flex: 1,
              editor: "textfield"
            },
            {
              text: __("To Primary"),
              dataIndex: "to_primary",
              flex: 1,
              editor: "textfield"
            }
          ]
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
              editor: "textfield"
            },
            {
              text: __("Value"),
              dataIndex: "value",
              flex: 1,
              editor: "numberfield"
            }
          ]
        }
      ],
      formToolbar: [
        {
          text: __("JSON"),
          glyph: NOC.glyph.file,
          tooltip: __("Show JSON"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onJSON
        }
      ]
    });
    me.callParent();
  },
  //
  onJSON: function() {
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord);
  }
});
