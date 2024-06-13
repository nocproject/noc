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
  initComponent: function(){
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
          text: __("Code"),
          dataIndex: "code",
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
          name: "code",
          xtype: "textfield",
          fieldLabel: __("Code"),
          allowBlank: false,
          uiStyle: "medium",
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
          allowBlank: false,
        },
        {
          name: "max_endpoints",
          xtype: "numberfield",
          fieldLabel: __("Max. Endpoints"),
          allowBlank: true,
          uiStyle: "medium",
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Hierarchy"),
          items: [
            {
              name: "allow_parent",
              xtype: "checkbox",
              boxLabel: __("Allow Parent"),
            },
            {
              name: "allow_children",
              xtype: "checkbox",
              boxLabel: __("Allow Children"),
            },
          ],
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Topology"),
          items: [
            {
              name: "allow_p2p",
              xtype: "checkbox",
              boxLabel: __("Allow P2P"),
            },
            {
              name: "allow_up2p",
              xtype: "checkbox",
              boxLabel: __("Allow Unidirectional P2P"),
            },
            {
              name: "allow_bunch",
              xtype: "checkbox",
              boxLabel: __("Allow Bunch"),
            },
            {
              name: "allow_p2mp",
              xtype: "checkbox",
              boxLabel: __("Allow P2MP"),
            },
            {
              name: "allow_up2pm",
              xtype: "checkbox",
              boxLabel: __("Allow Unidirectional P2MP"),
            },
            {
              name: "allow_star",
              xtype: "checkbox",
              boxLabel: __("Allow Star"),
            },
          ],
        },
        {
          name: "channel_discriminators",
          xtype: "gridfield",
          fieldLabel: __("Channel Discriminators"),
          allowBlank: true,
          columns: [
            {
              text: __("Discriminator"),
              dataIndex: "discriminator",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Required"),
              dataIndex: "is_required",
              width: 50,
              renderer: NOC.render.Bool,
              editor: "checkbox",
            },
            {
              text: __("Description"),
              dataIndex: "description",
              flex: 1,
              editor: "textfield",
            },
          ],
        },
        {
          name: "endpoint_discriminators",
          xtype: "gridfield",
          fieldLabel: __("Endpoint Discriminators"),
          allowBlank: true,
          columns: [
            {
              text: __("Discriminator"),
              dataIndex: "discriminator",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Required"),
              dataIndex: "is_required",
              width: 50,
              renderer: NOC.render.Bool,
              editor: "checkbox",
            },
            {
              text: __("Description"),
              dataIndex: "description",
              flex: 1,
              editor: "textfield",
            },
          ],
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
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord);
  },
});
