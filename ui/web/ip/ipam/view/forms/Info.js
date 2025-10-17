//---------------------------------------------------------------------
// ip.ipam info panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.Info");

Ext.define("NOC.ip.ipam.view.forms.Info", {
  extend: "Ext.panel.Panel",
  alias: "widget.ip.ipam.info",
  tpl: [
    "<div style='padding-bottom: 5px;'><b style='padding-right: 5px'>" + __("Name") + ":</b>{name}</div>",
    "<div style='padding-bottom: 5px;'><b style='padding-right: 5px'>" + __("Profile") + ":</b>{profile}</div>",
    "<div style='padding-bottom: 5px;'><b style='padding-right: 5px'>" + __("State") + ":</b>{state}</div>",
    "<div style='padding-bottom: 5px;'><b style='padding-right: 5px'>" + __("Maintainers") + ":</b>",
    "<span style='hyphens: auto;'>{[values.maintainers.join(' ')]}</span></div>",
    "<tpl foreach='info'><div style='padding-bottom: 5px;'><b style='padding-right: 5px'>{$}:</b>{.}<br/></div></tpl>",
  ],
});
