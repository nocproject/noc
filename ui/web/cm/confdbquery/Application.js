//---------------------------------------------------------------------
// cm.confdbquery application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.confdbquery.Application");

Ext.define("NOC.cm.confdbquery.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.CodeViewer",
    "NOC.core.JSONPreviewII",
    "NOC.cm.confdbquery.Model",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.cm.confdbquery.Model",
  search: true,

  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/cm/confdbquery/{0}/json/",
      previewName: "ConfDB Query: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 350,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          labelAlign: "top",
          allowBlank: false,
          uiStyle: "large",
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
          labelAlign: "top",
          allowBlank: true,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          labelAlign: "top",
          allowBlank: true,
        },
        {
          name: "params",
          xtype: "gridfield",
          fieldLabel: __("Parameters"),
          labelAlign: "top",
          columns: [
            {
              dataIndex: "name",
              text: __("Name"),
              editor: "textfield",
              width: 150,
            },
            {
              dataIndex: "type",
              text: __("Type"),
              width: 70,
              editor: {
                xtype: "combobox",
                store: [
                  ["str", "str"],
                  ["int", "int"],
                  ["bool", "bool"],
                  ["ip", "IP"],
                ],
              },
            },
            {
              dataIndex: "default",
              text: __("Default"),
              editor: "textfield",
              width: 200,
            },
            {
              dataIndex: "description",
              text: __("Description"),
              editor: "textfield",
              flex: 1,
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Allow"),
          layout: "hbox",
          defaults: {
            padding: 4,
          },
          items: [
            {
              name: "allow_object_filter",
              xtype: "checkbox",
              boxLabel: __("Object Filter"),
            },
            {
              name: "allow_object_validation",
              xtype: "checkbox",
              boxLabel: __("Object Validation"),
            },
            {
              name: "allow_interface_filter",
              xtype: "checkbox",
              boxLabel: __("Interface Filter"),
            },
            {
              name: "allow_interface_validation",
              xtype: "checkbox",
              boxLabel: __("Interface Validation"),
            },
          ],
        },
        {
          name: "require_raw",
          xtype: "checkbox",
          boxLabel: "Require raw",
        },
        {
          name: "source",
          xtype: "codeviewer",
          fieldLabel: __("Source"),
          labelAlign: "top",
          allowBlank: false,
          height: 400,
          // codeviewer config
          language: "python",
          readOnly: false,
          automaticLayout: true,
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
