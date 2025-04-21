//---------------------------------------------------------------------
// main.template application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.template.Application");

Ext.define("NOC.main.template.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.template.Model",
    "NOC.main.ref.messagetype.LookupField",
    "NOC.core.JSONPreviewII",
  ],
  model: "NOC.main.template.Model",
  search: true,
  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/main/template/{0}/json/",
      previewName: "Template: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 120,
        },
        {
          text: __("System"),
          dataIndex: "is_system",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Builtin"),
          dataIndex: "is_builtin",
          renderer: NOC.render.Bool,
          width: 30,
        },
        {
          text: __("Subject"),
          dataIndex: "subject",
          flex: 1,
        },
      ],
      fields: [
        {
          xtype: "container",
          layout: "hbox",
          items: [
            {
              name: "name",
              xtype: "textfield",
              fieldLabel: __("Name"),
              allowBlank: false,
              uiStyle: "large",
            },
            {
              name: "uuid",
              xtype: "displayfield",
              style: "padding-left: 10px",
              fieldLabel: __("UUID"),
            },
            {
              name: "is_system",
              xtype: "checkbox",
              boxLabel: __("System"),
              disabled: true,
            },
          ],
        },
        {
          name: "message_type",
          xtype: "main.ref.messagetype.LookupField",
          fieldLabel: __("Message Type"),
          //labelAlign: "left",
          allowBlank: true,
        },
        {
          name: "subject",
          xtype: "textareafield",
          fieldLabel: __("Subject"),
          allowBlank: false,
          anchor: "100%",
          height: 100,
          fieldStyle: {
            fontFamily: "Courier",
          },
        },
        {
          name: "body",
          xtype: "textareafield",
          fieldLabel: __("Body"),
          allowBlank: true,
          anchor: "100%",
          height: 200,
          fieldStyle: {
            fontFamily: "Courier",
          },
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
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },

  filters: [ ],
});
