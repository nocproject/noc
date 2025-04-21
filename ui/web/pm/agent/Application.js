//---------------------------------------------------------------------
// pm.agent application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.agent.Application");

Ext.define("NOC.pm.agent.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.core.StateField",
    "NOC.core.JSONPreviewII",
    "NOC.pm.agent.Model",
    "NOC.pm.agentprofile.LookupField",
  ],
  model: "NOC.pm.agent.Model",

  initComponent: function(){
    var me = this;

    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/pm/agent/{0}/config/",
      previewName: "Agent Config: {0}",
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 150,
        },
        {
          text: __("Profile"),
          dataIndex: "profile",
          width: 150,
          renderer: NOC.render.Lookup("profile"),
        },
        {
          text: __("State"),
          dataIndex: "state",
          width: 150,
          renderer: NOC.render.Lookup("state"),
        },
        {
          text: __("Labels"),
          dataIndex: "effective_labels",
          renderer: NOC.render.LabelField,
          width: 300,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          uiStyle: "extra",
          allowBlank: true,
        },
        {
          name: "profile",
          xtype: "pm.agentprofile.LookupField",
          fieldLabel: __("Profile"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          name: "zk_check_interval",
          xtype: "numberfield",
          fieldLabel: __("Check Interval"),
          uiStyle: "medium",
          allowBlank: true,
        },
        {
          name: "state",
          xtype: "statefield",
          fieldLabel: __("State"),
          allowBlank: true,
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
          allowBlank: true,
          query: {
            "enable_agent": true,
          },
        },
        {
          name: "bi_id",
          xtype: "displayfield",
          fieldLabel: __("BI ID"),
          allowBlank: true,
          uiStyle: "medium",
        },
        {
          name: "key",
          xtype: "displayfield",
          fieldLabel: __("Key"),
          allowBlank: true,
        },
        {
          name: "serial",
          xtype: "textfield",
          fieldLabel: __("Serial"),
          allowBlank: true,
        },
        {
          name: "ip",
          xtype: "gridfield",
          fieldLabel: __("IP"),
          columns: [
            {
              name: __("IP"),
              dataIndex: "ip",
              editor: "textfield",
              flex: 1,
            },
          ],
        },
        {
          name: "mac",
          xtype: "gridfield",
          fieldLabel: __("MAC"),
          columns: [
            {
              name: __("MAC"),
              dataIndex: "mac",
              editor: "textfield",
              flex: 1,
            },
          ],
        },
      ],
      formToolbar: [
        {
          text: __("Config"),
          glyph: NOC.glyph.file,
          tooltip: __("Show Config"),
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