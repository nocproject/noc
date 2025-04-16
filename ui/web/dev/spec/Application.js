//---------------------------------------------------------------------
// dev.spec application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dev.spec.Application");

Ext.define("NOC.dev.spec.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.core.ListFormField",
    "NOC.dev.spec.Model",
    "NOC.dev.quiz.LookupField",
    "NOC.sa.profile.LookupField",
  ],
  model: "NOC.dev.spec.Model",
  search: true,

  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/dev/spec/{0}/json/",
      previewName: "Spec: {0}",
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
          text: __("Quiz"),
          dataIndex: "quiz",
          width: 150,
          renderer: NOC.render.Lookup("quiz"),
        },
        {
          text: __("Profile"),
          dataIndex: "profile",
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
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
          allowBlank: true,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: false,
        },
        {
          name: "revision",
          xtype: "numberfield",
          fieldLabel: __("Revision"),
          allowBlank: false,
          minValue: 1,
          uiStyle: "small",
        },
        {
          name: "quiz",
          xtype: "dev.quiz.LookupField",
          fieldLabel: __("Quiz"),
          allowBlank: false,
        },
        {
          name: "profile",
          xtype: "sa.profile.LookupField",
          fieldLabel: __("Profile"),
          allowBlank: false,
        },
        {
          name: "author",
          xtype: "textfield",
          fieldLabel: __("Author"),
          allowBlank: false,
        },
        {
          name: "changes",
          xtype: "listform",
          fieldLabel: __("Changes"),
          items: [
            {
              name: "date",
              xtype: "textfield",
              fieldLabel: __("Date"),
              allowBlank: false,
              uiStyle: "medium",
            },
            {
              name: "changes",
              xtype: "textarea",
              fieldLabel: __("Changes"),
              allowBlank: false,
              uiStyle: "extra",
            },
          ],
        },
        {
          name: "answers",
          xtype: "listform",
          fieldLabel: __("Answers"),
          allowBlank: false,
          items: [
            {
              name: "name",
              xtype: "textfield",
              fieldLabel: __("Name"),
              allowBlank: false,
              uiStyle: "medium",
            },
            {
              name: "type",
              xtype: "combobox",
              fieldLabel: __("Type"),
              allowBlank: false,
              uiStyle: "medium",
              store: [
                ["str", "str"],
                ["bool", "bool"],
                ["int", "int"],
                ["cli", "cli"],
                ["snmp-get", "snmp-get"],
                ["snmp-getnext", "snmp-getnext"],
              ],
            },
            {
              name: "value",
              xtype: "textarea",
              fieldLabel: __("Value"),
              allowBlank: false,
              uiStyle: "extra",
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

  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
