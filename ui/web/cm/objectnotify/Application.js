//---------------------------------------------------------------------
// cm.objectnotify application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.objectnotify.Application");

Ext.define("NOC.cm.objectnotify.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.cm.objectnotify.Model",
    "NOC.core.combotree.ComboTree",
    "NOC.cm.objectnotify.LookupField",
    "NOC.main.notificationgroup.LookupField",
  ],
  model: "NOC.cm.objectnotify.Model",
  recordReload: true,
  maskElement: "el",
  initComponent: function(){
    var me = this;
    me.typeField = Ext.create({xtype: "cm.objectnotify.LookupField"});
    Ext.apply(me, {
      columns: [
        {
          text: __("Type"),
          dataIndex: "type",
          renderer: me.type_render,
          width: 200,
        },
        {
          text: __("Adm. Domain"),
          dataIndex: "administrative_domain",
          renderer: NOC.render.Lookup("administrative_domain"),
          width: 200,
        },
        {
          text: __("Notification Group"),
          dataIndex: "notification_group",
          renderer: NOC.render.Lookup("notification_group"),
          width: 200,
        },
        {
          text: __("Immediately"),
          dataIndex: "notify_immediately",
          width: 100,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Delayed"),
          dataIndex: "notify_delayed",
          width: 100,
          renderer: NOC.render.Bool,
        },
      ],
      fields: [
        {
          xtype: "cm.objectnotify.LookupField",
          fieldLabel: __("Type"),
          name: "type",
          uiStyle: "medium",
        },
        {
          xtype: "noc.core.combotree",
          restUrl: "/sa/administrativedomain/",
          fieldLabel: __("Adm. Domain"),
          name: "administrative_domain",
          allowBlank: true,
          uiStyle: "large",
        },
        {
          name: "notify_immediately",
          xtype: "checkboxfield",
          boxLabel: __("Notify Immediately"),
          boxLabelAlign: "before",
          allowBlank: false,
          uiStyle: "small",
        },
        {
          name: "notify_delayed",
          xtype: "checkboxfield",
          boxLabel: __("Notify Delayed"),
          boxLabelAlign: "before",
          allowBlank: false,
          uiStyle: "small",
        },
        {
          name: "notification_group",
          xtype: "main.notificationgroup.LookupField",
          fieldLabel: __("Notification Group"),
          width: 400,
          allowBlank: true,
          uiStyle: "medium",
        },
      ],
    });
    me.callParent();
  },
  filters: [
    {
      title: __("By Immediately"),
      name: "notify_immediately",
      ftype: "boolean",
    },
    {
      title: __("By Delayed"),
      name: "notify_delayed",
      ftype: "boolean",
    },
    {
      title: __("By Adm. Domain"),
      name: "administrative_domain",
      ftype: "tree",
      lookup: "sa.administrativedomain",
    },
    {
      title: __("By Type"),
      name: "type",
      ftype: "lookup",
      lookup: "cm.objectnotify",
    },
  ],
  type_render: function(value){
    return this.up().typeField.getStore().findRecord("value", value).get("text");
  },
});