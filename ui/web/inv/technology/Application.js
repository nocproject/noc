//---------------------------------------------------------------------
// inv.technology application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.technology.Application");

Ext.define("NOC.inv.technology.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.inv.technology.Model",
    "NOC.main.ref.modelid.LookupField",
  ],
  model: "NOC.inv.technology.Model",
  search: true,
  helpId: "reference-technology",

  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/inv/technology/{0}/json/",
      previewName: "Technology: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    me.cardButton = Ext.create("Ext.button.Button", {
      text: __("Card"),
      glyph: NOC.glyph.eye,
      scope: me,
      handler: me.onCard,
    });

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 150,
        },
        {
          text: __("Service Model"),
          dataIndex: "service_model",
          width: 150,
        },
        {
          text: __("Client Model"),
          dataIndex: "client_model",
          width: 150,
        },
        {
          text: __("Single Service"),
          dataIndex: "single_service",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Single Client"),
          dataIndex: "single_client",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Allow Children"),
          dataIndex: "allow_children",
          width: 50,
          renderer: NOC.render.Bool,
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
          name: "service_model",
          xtype: "main.ref.modelid.LookupField",
          fieldLabel: __("Service Model"),
          allowBlank: true,
        },
        {
          name: "client_model",
          xtype: "main.ref.modelid.LookupField",
          fieldLabel: __("Client Model"),
          allowBlank: true,
        },
        {
          name: "single_service",
          xtype: "checkbox",
          boxLabel: __("Single Service"),
        },
        {
          name: "single_client",
          xtype: "checkbox",
          boxLabel: __("Single Client"),
        },
        {
          name: "allow_children",
          xtype: "checkbox",
          boxLabel: __("Allow Children"),
        },
      ],
      formToolbar: [
        me.cardButton,
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
  //
  onCard: function(){
    var me = this;
    if(me.currentRecord){
      window.open(
        "/api/card/view/technology/" + me.currentRecord.get("id") + "/",
      );
    }
  },
});
