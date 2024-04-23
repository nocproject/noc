//---------------------------------------------------------------------
// inv.techdomain application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.techdomain.Application");

Ext.define("NOC.inv.techdomain.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.inv.techdomain.Model"],
  model: "NOC.inv.techdomain.Model",
  search: true,
  initComponent: function () {
    var me = this;
    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: new Ext.XTemplate("/inv/techdomain/{id}/json/"),
      previewName: new Ext.XTemplate("Object Model: {name}"),
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    //
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
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
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "kind",
          xtype: "combobox",
          fieldLabel: __("Kind"),
          uiStyle: "medium",
          store: [
            ["l1", "Level 1"],
            ["l2", "Level 2"],
            ["l3", "Level 3"],
            ["internet", "Internet"],
          ],
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Settings"),
          items: [
            {
              name: "max_endpoints",
              xtype: "numberfield",
              fieldLabel: __("Max. Endpoints"),
              allowBlank: true,
            },
            {
              name: "full_mesh",
              xtype: "checkbox",
              boxLabel: __("Full Mesh"),
            },
            {
              name: "require_unique",
              xtype: "checkbox",
              boxLabel: __("Require Unique"),
            },
          ],
        },
        {
          name: "discriminators",
          xtype: "gridfield",
          fieldLabel: __("Discriminators"),
          columns: [
            {
              text: __("Discriminators"),
              dataIndex: "name",
              editor: "textfield",
              width: 100
            },
            {
              text: __("Required"),
              dataIndex: "is_required",
              renderer: NOC.render.Bool,
              editor: "checkbox",
              width: 50
            },
            {
              text: __("Description"),
              dataIndex: "description",
              editor: "textfield",
              flex: 1
            }
          ]
        },
        {
          name: "bi_id",
          xtype: "displayfield",
          fieldLabel: __("BI ID"),
          allowBlank: true,
          uiStyle: "medium",
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
  onJSON: function () {
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord);
  },
});
