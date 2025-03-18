// fm.reportmovedmac application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportmovedmac.Application");

Ext.define("NOC.inv.reportmovedmac.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.core.ReportControl",
    "NOC.inv.networksegment.TreeCombo",
    "NOC.inv.interfaceprofile.LookupField",
    "NOC.inv.resourcegroup.TreeCombo",
    "NOC.sa.administrativedomain.TreeCombo",
  ],

  items: {
    xtype: "report.control",
    url: "/inv/reportmovedmac",
    controls: [
      {
        name: "from_date",
        xtype: "datefield",
        startDay: 1,
        fieldLabel: __("From"),
        allowBlank: false,
        format: "d.m.Y",
        submitFormat: "d.m.Y",
      },
      {
        name: "to_date",
        xtype: "datefield",
        startDay: 1,
        fieldLabel: __("To"),
        allowBlank: false,
        format: "d.m.Y",
        submitFormat: "d.m.Y",
      },
      {
        name: "segment",
        xtype: "inv.networksegment.TreeCombo",
        fieldLabel: __("Segment"),
        listWidth: 1,
        listAlign: "left",
        labelAlign: "left",
        width: 500,
      },
      {
        name: "administrative_domain",
        xtype: "sa.administrativedomain.TreeCombo",
        fieldLabel: __("By Adm. domain"),
        listWidth: 1,
        listAlign: "left",
        labelAlign: "left",
        width: 500,
        allowBlank: true,
      },
      {
        name: "resource_group",
        xtype: "inv.resourcegroup.TreeCombo",
        fieldLabel: __("By Resource Group (Selector)"),
        listWidth: 1,
        listAlign: "left",
        labelAlign: "left",
        width: 500,
        allowBlank: true,
      },
      {
        name: "interface_profile",
        xtype: "inv.interfaceprofile.LookupField",
        fieldLabel: __("By Interface Profile"),
        listWidth: 1,
        listAlign: "left",
        labelAlign: "left",
        width: 500,
        allowBlank: true,
      },
      {
        name: "exclude_serial_change",
        xtype: "checkboxfield",
        boxLabel: __("Exclude Device if SerialNumber changed"),
        checked: true,
        allowBlank: false,
      },
      {
        name: "enable_autowidth",
        xtype: "checkboxfield",
        boxLabel: __("Enable Excel column autowidth"),
        allowBlank: false,
      },
    ],
    storeData: [
      ["object_name", __("Object Name"), true],
      ["object_address", __("Object  Address"), true],
      ["object_adm_domain", __("Object Adm. Domain"), true],
      ["event_type", __("Event Type (Migrate/Duplicate)"), true],
      ["sn_changed", __("Device SN changed (by BI)"), true],
      ["vendor_mac", __("Vendor MAC"), true],
      ["mac", __("MAC"), true],
      ["migrate_ts", __("Migrate TS"), true],
      ["from_iface_name", __("From Interface Name"), true],
      ["from_iface_down", __("From Interface Down"), true],
      ["to_iface_name", __("To Interface Name"), true],
      ["to_iface_down", __("To Interface Down"), true],
    ],
  },
});

