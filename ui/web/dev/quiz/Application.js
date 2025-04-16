//---------------------------------------------------------------------
// dev.quiz application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dev.quiz.Application");

Ext.define("NOC.dev.quiz.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.ListFormField",
    "NOC.core.JSONPreviewII",
    "NOC.dev.quiz.Model",
  ],
  model: "NOC.dev.quiz.Model",
  search: true,

  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/dev/quiz/{0}/json/",
      previewName: "Quiz: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
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
          name: "disclaimer",
          xtype: "textarea",
          fieldLabel: __("Disclaimer"),
          allowBlank: true,
        },
        {
          name: "questions",
          xtype: "listform",
          fieldLabel: __("Questions"),
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
              name: "question",
              xtype: "textarea",
              fieldLabel: __("Question"),
              allowBlank: false,
              uiStyle: "extra",
            },
            {
              name: "when",
              xtype: "textfield",
              fieldLabel: __("When"),
              allowBlank: true,
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

  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
