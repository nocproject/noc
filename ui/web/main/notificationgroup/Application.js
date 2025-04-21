//---------------------------------------------------------------------
// main.notificationgroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.notificationgroup.Application");

Ext.define("NOC.main.notificationgroup.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.core.ListFormField",
    "NOC.core.tagfield.Tagfield",
    "NOC.core.label.LabelField",
    "NOC.main.notificationgroup.Model",
    "NOC.main.timepattern.LookupField",
    "NOC.main.template.LookupField",
    "NOC.main.ref.messagetype.LookupField",
    "NOC.aaa.user.LookupField",
    "NOC.aaa.group.LookupField",
    "NOC.inv.resourcegroup.LookupField",
    "NOC.sa.administrativedomain.LookupField",
  ],
  model: "NOC.main.notificationgroup.Model",
  search: true,
  helpId: "reference-notification-group",
  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/main/notificationgroup/{0}/json/",
      previewName: "Notification Group: {0}",
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 250,
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
          text: __("Description"),
          dataIndex: "description",
          width: 350,
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
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
          allowBlank: true,
        },
        {
          name: "message_register_policy",
          xtype: "combobox",
          fieldLabel: __("Message Registry Policy"),
          allowBlank: true,
          store: [
            ["d", __("Disabled")],
            ["a", __("Any")],
            ["t", __("By Types")],
          ],
        },
        {
          name: "message_types",
          fieldLabel: __("Message Types"),
          xtype: "gridfield",
          columns: [
            {
              text: __("Message Type"),
              dataIndex: "message_type",
              width: 150,
              renderer: NOC.render.Lookup("message_type"),
              editor: "main.ref.messagetype.LookupField",
            },
            {
              text: __("Template"),
              dataIndex: "template",
              width: 350,
              renderer: NOC.render.Lookup("template"),
              editor: "main.template.LookupField",
            },
          ],
        },
        {
          name: "static_members",
          fieldLabel: __("Static Members"),
          xtype: "gridfield",
          columns: [
            {
              text: __("Time Pattern"),
              dataIndex: "time_pattern",
              width: 350,
              renderer: NOC.render.Lookup("time_pattern"),
              editor: "main.timepattern.LookupField",
            },
            {
              text: __("Method"),
              dataIndex: "notification_method",
              width: 75,
              editor: {
                xtype: "combobox",
                store: [
                  ["mail", "Mail"],
                  ["tg", "Telegram"],
                  ["icq", "ICQ"],
                  ["file", "File"],
                  ["xmpp", "Jabber"],
                ],
              },
            },
            {
              text: __("Contact"),
              dataIndex: "contact",
              width: 300,
              editor: "textfield",
            },
          ],
        },
        {
          name: "subscription_settings",
          xtype: "gridfield",
          fieldLabel: __("Subscription Settings"),
          columns: [
            {
              text: __("User"),
              dataIndex: "user",
              editor: "aaa.user.LookupField",
              renderer: NOC.render.Lookup("user"),
              width: 250,
            },
            {
              text: __("Group"),
              dataIndex: "group",
              editor: "aaa.group.LookupField",
              renderer: NOC.render.Lookup("group"),
              width: 250,
            },
            {
              text: __("Allow Subscribe"),
              dataIndex: "allow_subscribe",
              editor: "checkboxfield",
              width: 100,
              renderer: NOC.render.Bool,
            },
            {
              text: __("Add to Subscription"),
              dataIndex: "auto_subscription",
              editor: "checkboxfield",
              width: 100,
              renderer: NOC.render.Bool,
            },
            {
              text: __("Notify Changed"),
              dataIndex: "notify_if_subscribed",
              editor: "checkboxfield",
              width: 100,
              renderer: NOC.render.Bool,
            },
          ],
        },
        {
          name: "conditions",
          xtype: "listform",
          fieldLabel: __("Match Conditions"),
          rows: 5,
          items: [
            {
              name: "labels",
              xtype: "labelfield",
              fieldLabel: __("Match Labels"),
              allowBlank: true,
              isTree: true,
              pickerPosition: "down",
              uiStyle: "extra",
              query: {
                "allow_matched": true,
              },
            },
            {
              xtype: "core.tagfield",
              url: "/inv/resourcegroup/lookup/",
              fieldLabel: __("Object Groups"),
              name: "resource_groups",
            },
            {
              name: "administrative_domain",
              xtype: "sa.administrativedomain.LookupField",
              fieldLabel: __("Adm. Domain"),
              allowBlank: true,
            },
          ],
        },
      ],
      actions: [
        {
          title: __("Test selected groups"),
          action: "test",
          form: [
            {
              name: "subject",
              xtype: "textfield",
              fieldLabel: __("Subject"),
              allowBlank: false,
              width: 600,
            },
            {
              name: "body",
              xtype: "textarea",
              fieldLabel: __("Body"),
              allowBlank: false,
              width: 600,
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
