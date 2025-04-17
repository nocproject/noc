//---------------------------------------------------------------------
// wf.transition application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.transition.Application");

Ext.define("NOC.wf.transition.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.wf.transition.Model",
    "NOC.core.JSONPreviewII",
    "NOC.wf.workflow.LookupField",
    "NOC.wf.state.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.core.label.LabelField",
    "NOC.core.ListFormField",
    "Ext.ux.form.StringsField",
  ],
  model: "NOC.wf.transition.Model",
  initComponent: function(){
    var me = this;
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/wf/transition/{0}/json/",
      previewName: "Workflow Transition: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Workflow"),
          dataIndex: "workflow",
          width: 200,
          renderer: NOC.render.Lookup("workflow"),
        },
        {
          text: __("From State"),
          dataIndex: "from_state",
          width: 200,
          renderer: NOC.render.Lookup("from_state"),
        },
        {
          text: __("To State"),
          dataIndex: "to_state",
          width: 200,
          renderer: NOC.render.Lookup("to_state"),
        },
        {
          text: __("Active"),
          dataIndex: "is_active",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Manual"),
          dataIndex: "enable_manual",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Event"),
          dataIndex: "event",
          width: 100,
        },
        {
          text: __("Label"),
          dataIndex: "label",
          flex: 1,
        },
      ],

      fields: [
        {
          name: "workflow",
          xtype: "wf.workflow.LookupField",
          fieldLabel: __("Workflow"),
          allowBlank: true,
        },
        {
          name: "from_state",
          xtype: "wf.state.LookupField",
          fieldLabel: __("From State"),
          allowBlank: false,
        },
        {
          name: "to_state",
          xtype: "wf.state.LookupField",
          fieldLabel: __("To State"),
          allowBlank: false,
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
        },
        {
          name: "label",
          xtype: "textfield",
          fieldLabel: __("Label"),
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "event",
          xtype: "textfield",
          fieldLabel: __("Event"),
          allowBlank: true,
          uiStyle: "medium",
        },
        {
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Active"),
        },
        {
          name: "enable_manual",
          xtype: "checkbox",
          boxLabel: __("Enable Manual"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "right",
          },
          items: [
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "remote_id",
              xtype: "textfield",
              fieldLabel: __("Remote ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "bi_id",
              xtype: "displayfield",
              fieldLabel: __("BI ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
          ],
        },
        {
          name: "handlers",
          xtype: "stringsfield",
          fieldLabel: __("Handlers"),
          allowBlank: true,
        },
        {
          name: "required_rules",
          xtype: "listform",
          fieldLabel: __("Required Rules"),
          rows: 3,
          items: [
            {
              name: "labels",
              xtype: "labelfield",
              fieldLabel: __("Match Labels"),
              allowBlank: true,
              isTree: true,
              filterProtected: false,
              pickerPosition: "down",
              uiStyle: "extra",
              query: {
                "allow_matched": true,
              },
            },
            {
              name: "exclude_labels",
              xtype: "labelfield",
              fieldLabel: __("Exclude Match Labels"),
              allowBlank: true,
              isTree: true,
              filterProtected: false,
              pickerPosition: "down",
              uiStyle: "extra",
              query: {
                "allow_matched": true,
              },
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
  filters: [
    {
      title: __("By Workflow"),
      name: "workflow",
      ftype: "lookup",
      lookup: "wf.workflow",
    },
    {
      title: __("By From"),
      name: "from_state",
      ftype: "lookup",
      lookup: "wf.state",
    },
    {
      title: __("By To"),
      name: "to_state",
      ftype: "lookup",
      lookup: "wf.state",
    },
  ],
  //
  onJSON: function(){
    var me = this,
      record = new Ext.data.Model({
        id: me.currentRecord.id,
        name: me.currentRecord.get("workflow__label"),
      });
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(record, me.ITEM_FORM);
  },
});
