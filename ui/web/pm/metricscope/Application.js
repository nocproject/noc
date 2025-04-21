//---------------------------------------------------------------------
// pm.metricscope application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricscope.Application");

Ext.define("NOC.pm.metricscope.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.pm.metricscope.Model",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.pm.metricscope.Model",
  search: true,
  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/pm/metricscope/{0}/json/",
      previewName: "Scope: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: "Name",
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
          name: "table_name",
          xtype: "textfield",
          fieldLabel: __("Table"),
          allowBlank: false,
          uiStyle: "medium",
          regex: /[a-zA-Z][0-9a-zA-Z_]*/,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "key_fields",
          xtype: "gridfield",
          fieldLabel: __("Key Fields"),
          allowBlank: false,
          columns: [
            {
              dataIndex: "field_name",
              text: __("Field"),
              width: 150,
              editor: "textfield",
            },
            {
              dataIndex: "model",
              text: __("Model"),
              flex: 1,
              editor: "textfield",
            },
          ],
        },
        {
          name: "labels",
          xtype: "gridfield",
          fieldLabel: __("Labels"),
          allowBlank: true,
          columns: [
            {
              dataIndex: "label",
              text: __("Label"),
              width: 150,
              editor: "textfield",
            },
            {
              dataIndex: "is_required",
              text: __("Required"),
              width: 50,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              dataIndex: "is_key_label",
              text: __("Include key Label"),
              width: 50,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              dataIndex: "is_primary_key",
              text: __("Primary Key"),
              width: 50,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              dataIndex: "is_order_key",
              text: __("Order Key"),
              width: 50,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              dataIndex: "is_path",
              text: __("Path"),
              width: 50,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              dataIndex: "store_column",
              text: __("Store Column"),
              flex: 1,
              editor: "textfield",
            },
            {
              dataIndex: "view_column",
              text: __("View Column"),
              flex: 1,
              editor: "textfield",
            },
          ],
        },
        {
          name: "enable_timedelta",
          xtype: "checkbox",
          boxLabel: __("Enable Time Delta (Require migration)"),
          tooltip: __(
            "Required run migration metric Database after changed." +
                        "That enabled only by deploy.",
          ),
          disabled: true,
          listeners: {
            render: me.addTooltip,
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
  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
