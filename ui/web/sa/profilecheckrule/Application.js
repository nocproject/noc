//---------------------------------------------------------------------
// sa.profilecheckrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.profilecheckrule.Application");

Ext.define("NOC.sa.profilecheckrule.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.sa.profilecheckrule.Model",
    "NOC.sa.profile.LookupField",
  ],
  model: "NOC.sa.profilecheckrule.Model",
  search: true,
  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/sa/profilecheckrule/{0}/json/",
      previewName: "Profile Check Rule: {0}",
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Profile Check Rule Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Blt"),
          // tooltip: "Built-in", - broken in ExtJS 5.1
          dataIndex: "is_builtin",
          width: 40,
          renderer: NOC.render.Bool,
          align: "center",
        },
        {
          text: __("Pref."),
          // tooltip: "Preference", - broken in ExtJS 5.1
          dataIndex: "preference",
          width: 40,
          align: "right",
        },
        {
          text: __("Method"),
          dataIndex: "method",
          width: 100,
        },
        {
          text: __("Parameter"),
          dataIndex: "param",
          width: 180,
        },
        {
          text: __("Match"),
          dataIndex: "match_method",
          width: 50,
          align: "center",
        },
        {
          text: __("Value"),
          dataIndex: "value",
          width: 200,
        },
        {
          text: __("Action"),
          dataIndex: "action",
          width: 50,
        },
        {
          text: __("Profile"),
          dataIndex: "profile",
          flex: 1,
          width: 150,
          renderer: NOC.render.Lookup("profile"),
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "large",
        },
        {
          xtype: "displayfield",
          name: "uuid",
          fieldLabel: __("UUID"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
        },
        {
          name: "preference",
          xtype: "numberfield",
          fieldLabel: __("Preference"),
          allowBlank: true,
          uiStyle: "small",
        },
        {
          xtype: "fieldset",
          title: __("Match"),
          layout: "hbox",
          defaults: {
            labelAlign: "top",
            padding: 4,
          },
          items: [
            {
              name: "method",
              xtype: "combobox",
              fieldLabel: __("Method"),
              store: [
                ["snmp_v2c_get", "snmp_v2c_get"],
                ["http_get", "http_get"],
                ["https_get", "https_get"],
              ],
              queryMode: "local",
              allowBlank: false,
              uiStyle: "medium",
            },
            {
              name: "param",
              xtype: "textfield",
              fieldLabel: __("Parameter"),
              allowBlank: false,
              uiStyle: "large",
            },
            {
              name: "match_method",
              xtype: "combobox",
              fieldLabel: __("Match"),
              store: [
                ["eq", "equals"],
                ["contains", "contains"],
                ["re", "regexp"],
              ],
              queryMode: "local",
              uiStyle: "small",
              allowBlank: false,
            },
            {
              name: "value",
              xtype: "textfield",
              fieldLabel: __("Value"),
              allowBlank: false,
              uiStyle: "large",
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Action"),
          layout: "hbox",
          defaults: {
            labelAlign: "top",
            padding: 4,
          },
          items: [
            {
              name: "action",
              xtype: "combobox",
              fieldLabel: __("Action"),
              store: [
                ["match", "Match"],
                ["maybe", "Maybe"],
              ],
              queryMode: "local",
              uiStyle: "medium",
              allowBlank: false,
            },
            {
              name: "profile",
              xtype: "sa.profile.LookupField",
              fieldLabel: __("Profile"),
              allowBlank: false,
              uiStyle: "medium",
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
      filters: [
        {
          title: __("By Profile"),
          name: "profile",
          ftype: "lookup",
          lookup: "sa.profile",
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
});
