//---------------------------------------------------------------------
// dns.dnszone application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszone.Application");

Ext.define("NOC.dns.dnszone.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.dns.dnszone.Model",
    "NOC.dns.dnszone.RecordsModel",
    "NOC.dns.dnszone.RRTypeField",
    "NOC.dns.dnszoneprofile.LookupField",
    "NOC.main.notificationgroup.LookupField",
    "NOC.project.project.LookupField",
  ],
  model: "NOC.dns.dnszone.Model",
  search: true,
  helpId: "reference-dns-zone",

  initComponent: function(){
    var me = this;

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Gen."),
          dataIndex: "is_auto_generated",
          renderer: NOC.render.Bool,
          width: 30,
        },
        {
          text: __("Type"),
          dataIndex: "type",
          renderer: NOC.render.Choices({
            "F": __("Fwd"),
            "4": __("Rev IPv4"),
            "6": __("Rev IPv6"),
          }),
          width: 30,
        },
        {
          text: __("Serial"),
          dataIndex: "serial",
          width: 75,
        },
        {
          text: __("Profile"),
          dataIndex: "profile",
          renderer: NOC.render.Lookup("profile"),
          width: 100,
        },
        {
          text: __("Project"),
          dataIndex: "project",
          renderer: NOC.render.Lookup("project"),
          width: 150,
        },
        {
          text: __("Paid Till"),
          dataIndex: "paid_till",
          width: 100,
          format: "Y-m-d",
          startDay: 1,
          renderer: NOC.render.Date,
        },
        {
          text: __("Notification"),
          dataIndex: "notification_group",
          renderer: NOC.render.Lookup("notification_group"),
          width: 100,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
        {
          text: __("Labels"),
          dataIndex: "labels",
          renderer: NOC.render.LabelField,
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Domain"),
          allowBlank: false,
          autoFocus: true,
        },
        {
          name: "description",
          xtype: "textfield",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "is_auto_generated",
          xtype: "checkboxfield",
          boxLabel: __("Auto generated?"),
          allowBlank: false,
        },
        {
          name: "serial",
          xtype: "displayfield",
          fieldLabel: __("Serial"),
          allowBlank: false,
        },
        {
          name: "profile",
          xtype: "dns.dnszoneprofile.LookupField",
          fieldLabel: __("Profile"),
          allowBlank: false,
        },
        {
          name: "project",
          xtype: "project.project.LookupField",
          fieldLabel: __("Project"),
          allowBlank: true,
        },
        {
          name: "notification_group",
          xtype: "main.notificationgroup.LookupField",
          fieldLabel: __("Notification Group"),
          allowBlank: true,
        },
        {
          name: "paid_till",
          xtype: "datefield",
          startDay: 1,
          fieldLabel: __("Paid Till"),
          allowBlank: true,
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
          allowBlank: true,
          query: {
            "allow_models": ["dns.DNSZone"],
          },
        },
      ],
      inlines: [
        {
          title: __("Records"),
          model: "NOC.dns.dnszone.RecordsModel",
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("TTL"),
              dataIndex: "ttl",
              width: 90,
              align: "right",
              editor: "numberfield",
            },
            {
              text: __("Type"),
              dataIndex: "type",
              width: 100,
              editor: {
                xtype: "dns.dnszone.RRTypeField",
                listeners: {
                  scope: me,
                  select: me.onSelectRRType,
                },
              },
            },
            {
              text: __("Prio."),
              dataIndex: "priority",
              width: 75,
              align: "right",
              editor: "numberfield",
            },
            {
              text: __("Content"),
              dataIndex: "content",
              flex: 1,
              editor: {
                xtype: "textfield",
                allowBlank: false,
              },
            },
            {
              text: __("Labels"),
              dataIndex: "labels",
              width: 150,
              editor: "labelfield",
            },
          ],
        },
      ],
      formToolbar: [
        {
          text: __("Preview"),
          glyph: NOC.glyph.search,
          tooltip: __("Preview zone"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onPreviewZone,
        },
      ],
    });
    me.callParent();
  },
  filters: [
    {
      title: __("By Profile"),
      name: "profile",
      ftype: "lookup",
      lookup: "dns.dnszoneprofile",
    },
    {
      title: __("By Type"),
      name: "type",
      ftype: "choices",
      store: [
        ["F", __("Forward")],
        ["4", __("IPv4 Reverse")],
        ["6", __("IPv6 Reverse")],
      ],
    },
    {
      title: __("By Project"),
      name: "project",
      ftype: "lookup",
      lookup: "project.project",
    },
    {
      title: __("By Notification"),
      name: "notification_group",
      ftype: "lookup",
      lookup: "main.notificationgroup",
    },
    {
      title: __("By Labels"),
      name: "labels",
      ftype: "label",
    },
  ],
  preview: {
    previewName: "Zone: {0}",
    restUrl: "/dns/dnszone/{0}/repo/zone/",
    xtype: "NOC.core.MonacoPanel",
  },
  // Check RRType accepts priority field
  isPriorityVisible: function(rrType){
    return (
      (rrType === "MX") ||
            (rrType === "SRV")
    );
  },

  onSelectRRType: function(combo){
    var me = this,
      rrType = combo.getValue(),
      priorityCombo = combo.ownerCt.items.items[3];
    priorityCombo.setDisabled(!me.isPriorityVisible(rrType));
  },

  onInlineBeforeEdit: function(plugin, context){
    var me = this,
      priorityCombo = plugin.editor.items.items[3];
    me.callParent(arguments);
    priorityCombo.setDisabled(!me.isPriorityVisible(context.record.get("type")));
  },
  onPreviewZone: function(){
    var me = this;
    me.previewItem(me.ITEM_PREVIEW, me.currentRecord);
  },
});
