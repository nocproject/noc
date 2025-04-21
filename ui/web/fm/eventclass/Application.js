//---------------------------------------------------------------------
// fm.eventclass application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.eventclass.Application");

Ext.define("NOC.fm.eventclass.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.fm.eventclass.Model",
    "NOC.fm.eventclass.LookupField",
    "NOC.fm.alarmclass.LookupField",
    "Ext.ux.form.JSONField",
    "Ext.ux.form.StringsField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.fm.eventclass.Model",
  search: true,
  treeFilter: "category",
  //
  initComponent: function(){
    var me = this;

    me.actionStore = Ext.create("Ext.data.Store", {
      fields: ["id", "label"],
      data: [
        {id: "D", label: "Drop"},
        {id: "L", label: "Log"},
        {id: "A", label: "Archive"},
      ],
    });
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 250,
        },
        {
          text: __("Builtin"),
          dataIndex: "is_builtin",
          renderer: NOC.render.Bool,
          width: 30,
        },
        {
          text: __("Description"),
          dataIndex: "description",
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
              fieldLabel: __("UUID"),
            },
          ],
        },
        {
          xtype: "tabpanel",
          layout: "fit",
          autoScroll: true,
          anchor: "-0, -50",
          defaults: {
            autoScroll: true,
            layout: "anchor",
          },
          items: [
            {
              title: __("Text"),
              items: [
                {
                  name: "description",
                  xtype: "textarea",
                  fieldLabel: __("Description"),
                  uiStyle: "extra",
                },
                {
                  name: "subject_template",
                  xtype: "textfield",
                  fieldLabel: __("Subject Template"),
                  uiStyle: "extra",
                  allowBlank: false,
                },
                {
                  name: "body_template",
                  xtype: "textarea",
                  fieldLabel: __("Body Template"),
                  uiStyle: "extra",
                  allowBlank: false,
                },
                {
                  name: "symptoms",
                  xtype: "textarea",
                  fieldLabel: __("Symptoms"),
                  uiStyle: "extra",
                  allowBlank: true,
                },
                {
                  name: "probable_causes",
                  xtype: "textarea",
                  fieldLabel: __("Probable Causes"),
                  uiStyle: "extra",
                  allowBlank: true,
                },
                {
                  name: "recommended_actions",
                  xtype: "textarea",
                  fieldLabel: __("Recommended Actions"),
                  uiStyle: "extra",
                  allowBlank: true,
                },
              ],
            },
            {
              title: __("Action"),
              items: [
                {
                  name: "action",
                  xtype: "combobox",
                  fieldLabel: __("Action"),
                  allowBlank: false,
                  store: me.actionStore,
                  queryMode: "local",
                  displayField: "label",
                  valueField: "id",
                },
                {
                  name: "link_event",
                  xtype: "checkboxfield",
                  boxLabel: __("Link Event"),
                },
              ],
            },
            {
              title: __("Variables"),
              items: [
                {
                  name: "vars",
                  xtype: "gridfield",
                  columns: [
                    {
                      text: __("Name"),
                      dataIndex: "name",
                      width: 100,
                      editor: "textfield",
                    },
                    {
                      text: __("Type"),
                      dataIndex: "type",
                      width: 100,
                      editor: {
                        xtype: "combobox",
                        store: [
                          "str",
                          "int", "float",
                          "ipv4_address", "ipv6_address", "ip_address",
                          "ipv4_prefix", "ipv6_prefix", "ip_prefix",
                          "mac", "interface_name", "oid",
                        ],
                      },
                    },
                    {
                      text: __("Required"),
                      dataIndex: "required",
                      width: 50,
                      editor: "checkboxfield",
                      renderer: NOC.render.Bool,
                    },
                    {
                      text: __("Suppression"),
                      dataIndex: "match_suppress",
                      width: 50,
                      editor: "checkboxfield",
                      renderer: NOC.render.Bool,
                    },
                    {
                      text: __("Description"),
                      dataIndex: "description",
                      flex: 1,
                      editor: "textfield",
                    },
                  ],
                },
              ],
            },
            {
              title: __("Disposition"),
              items: [
                {
                  name: "disposition",
                  xtype: "gridfield",
                  fieldLabel: __("Disposition"),
                  columns: [
                    {
                      text: __("Name"),
                      dataIndex: "name",
                      width: 100,
                      editor: "textfield",
                    },
                    {
                      text: __("Condition"),
                      dataIndex: "condition",
                      width: 100,
                      editor: "textfield",
                    },
                    {
                      text: __("Action"),
                      dataIndex: "action",
                      width: 70,
                      editor: {
                        xtype: "combobox",
                        store: [
                          "drop",
                          "ignore",
                          "raise",
                          "clear",
                        ],
                      },
                    },
                    {
                      text: __("Alarm"),
                      dataIndex: "alarm_class",
                      renderer: NOC.render.Lookup("alarm_class"),
                      width: 200,
                      editor: "fm.alarmclass.LookupField",
                    },
                    {
                      text: __("Stop"),
                      dataIndex: "stop_disposition",
                      renderer: NOC.render.Bool,
                      width: 50,
                      editor: "checkbox",
                    },
                    {
                      text: __("Managed Object"),
                      dataIndex: "managed_object",
                      editor: "textfield",
                      width: 100,
                    },
                    {
                      text: __("Var.  Map."),
                      dataIndex: "var_mapping",
                      renderer: NOC.render.JSON,
                      editor: "jsonfield",
                      flex: 1,
                    },
                  ],
                },
              ],
            },
            {
              title: __("Suppression"),
              items: [
                {
                  name: "deduplication_window",
                  xtype: "numberfield",
                  uiStyle: "small",
                  fieldLabel: __("Deduplication Window"),
                  allowBlank: false,
                },
                {
                  name: "suppression_window",
                  xtype: "numberfield",
                  uiStyle: "small",
                  fieldLabel: __("Suppression Window"),
                  allowBlank: false,
                },
                {
                  name: "ttl",
                  xtype: "numberfield",
                  uiStyle: "small",
                  fieldLabel: __("Event TTL"),
                  allowBlank: false,
                },
              ],
            },
            {
              title: __("Handlers"),
              items: [
                {
                  xtype: "stringsfield",
                  name: "handlers",
                  fieldLabel: __("Handlers"),
                },
              ],
            },
            {
              title: __("Plugins"),
              items: [
                {
                  xtype: "gridfield",
                  name: "plugins",
                  fieldLabel: __("Plugins"),
                  columns: [
                    {
                      text: __("Name"),
                      dataIndex: "name",
                      editor: "textfield",
                      width: 150,
                    },
                    {
                      text: __("Config"),
                      dataIndex: "config",
                      editor: "jsonfield",
                      flex: 1,
                      renderer: NOC.render.JSON,
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
      formToolbar: [
        {
          text: __("JSON"),
          glyph: NOC.glyph.file,
          tooltip: __("View as JSON"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onJSON,
        },
      ],
    });
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/fm/eventclass/{0}/json/",
      previewName: "Event Class: {0}",
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    me.callParent();
  },
  filters: [
    {
      title: __("By Link Event"),
      name: "link_event",
      ftype: "boolean",
    },
  ],
  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
