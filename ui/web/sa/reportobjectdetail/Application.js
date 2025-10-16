//---------------------------------------------------------------------
// fm.reportalarmdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.reportobjectdetail.Application");

Ext.define("NOC.sa.reportobjectdetail.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.core.ReportControl",
    "NOC.inv.networksegment.TreeCombo",
    "NOC.inv.resourcegroup.TreeCombo",
    "NOC.sa.administrativedomain.TreeCombo",
  ],

  items: {
    xtype: "report.control",
    url: "/sa/reportobjectdetail",
    controls: [
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
        name: "enable_autowidth",
        xtype: "checkboxfield",
        boxLabel: __("Enable Excel column autowidth"),
        allowBlank: false,
      },
    ],
    storeData: [
      ["id", __("ID"), false],
      ["object_name", __("Object Name"), true],
      ["object_address", __("IP"), true],
      ["object_hostname", __("Object Hostname"), true],
      ["object_status", __("Object Status"), true],
      ["profile_name", __("Profile"), true],
      ["object_profile", __("Object Profile"), false],
      ["object_vendor", __("Vendor"), false],
      ["object_platform", __("Platform"), false],
      ["object_attr_hwversion", __("Add. attributes: HW Version"), false],
      ["object_version", __("SW Version"), false],
      ["object_attr_bootprom", __("Add. attributes: BootPROM Version"), false],
      ["object_serial", __("Serial Number"), false],
      ["object_attr_patch", __("Add. attributes: sw. patch"), false],
      ["auth_profile", __("Auth Profile"), false],
      ["avail", __("Avail"), false],
      ["admin_domain", __("Admin. Domain"), true],
      ["container", __("Container"), false],
      ["segment", __("Segment"), true],
      ["phys_interface_count", __("Physical Iface Count"), false],
      ["link_count", __("Link Count"), false],
      ["last_config_ts", __("Last Config get Timestamp"), false],
      ["adm_path", __("Adm Path"), true],
      ["interface_type_count", __("Interface count by type"), false],
      ["object_caps", __("Object capabilities"), false],
      ["object_labels", __("Object Labels"), false],
      ["sorted_labels", __("Sorted Labels"), false],
      ["discovery_problem", __("Discovery Problem"), false],
      ["project", __("Project"), false],
    ],
  },
});
