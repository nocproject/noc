//---------------------------------------------------------------------
// inv.reportllinkdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportlinkdetail.Application");

Ext.define("NOC.inv.reportlinkdetail.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.core.ReportControl",
    "NOC.inv.networksegment.TreeCombo",
    'NOC.inv.resourcegroup.TreeCombo',
    "NOC.sa.administrativedomain.TreeCombo",
  ],

  items: {
    xtype: "report.control",
    url: "/inv/reportlinkdetail",
    controls: [
      {
        name: "segment",
        xtype: "inv.networksegment.TreeCombo",
        fieldLabel: __("Segment"),
        listWidth: 1,
        labelWidth: 250,
        listAlign: "left",
        labelAlign: "left",
        width: 650,
      },
      {
        name: "administrative_domain",
        xtype: "sa.administrativedomain.TreeCombo",
        fieldLabel: __("By Adm. domain"),
        listWidth: 1,
        labelWidth: 250,
        listAlign: "left",
        labelAlign: "left",
        width: 650,
        allowBlank: true,
      },
      {
        name: "resource_group",
        xtype: "inv.resourcegroup.TreeCombo",
        fieldLabel: __("By Resource Group (Selector)"),
        listWidth: 1,
        labelWidth: 250,
        listAlign: "left",
        labelAlign: "left",
        width: 650,
        allowBlank: true,
      },
      {
        name: "enable_autowidth",
        xtype: "checkboxfield",
        boxLabel: __("Enable Excel column autowidth"),
        allowBlank: false,
      },
    ],
    storeData: [
      ["object1_admin_domain", __("Admin. Domain"), true],
      ["object1_name", __("Object1 Name"), true],
      ["object1_address", __("IP1"), true],
      ["object1_platform", __("Object1 Platform"), false],
      ["object1_segment", __("Object1 Segment"), false],
      ["object1_tags", __("Object1 Tags"), false],
      ["object1_iface", __("Interface1"), true],
      ["object1_descr", __("Interface1 Description"), false],
      ["object1_speed", __("Interface1 Speed"), false],
      ["object2_admin_domain", __("Admin. Domain"), true],
      ["object2_name", __("Object2 Name"), true],
      ["object2_address", __("IP2"), true],
      ["object2_platform", __("Object2 Platform"), false],
      ["object2_segment", __("Object2 Segment"), false],
      ["object2_tags", __("Object2 Tags"), false],
      ["object2_iface", __("Interface2"), true],
      ["object2_descr", __("Interface2 Description"), false],
      ["object2_speed", __("Interface2 Speed"), false],
      ["link_proto", __("Link Proto"), true],
      ["last_seen", __("Link Last Seen"), false],
    ],
  },
});
