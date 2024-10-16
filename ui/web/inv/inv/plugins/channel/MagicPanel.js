//---------------------------------------------------------------------
// inv.inv Channel Magic Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.channel.MagicPanel");

Ext.define("NOC.inv.inv.plugins.channel.MagicPanel", {
  extend: "Ext.panel.Panel",
  alias: "widget.invchannelmagic",
  layout: "fit",
  defaultListenerScope: true,
  items: [
    {
      xtype: "grid",
      scrollable: "y",
      height: 310,
      allowDeselect: true,
      store: new Ext.data.Store({
        fields: ["controller", "start_endpoint", "start_endpoint__label", "end_endpoint", "end_endpoint__label"],
        data: [],
      }),
      columns: [
        {
          text: __("Channel"),
          dataIndex: "channel_name",
          width: 250,
          renderer: function(v){
            if(v){
              return v;
            }
            return "<i>" + __("Create new") + "</i>";
          },
        },
        {
          text: __("Start"),
          dataIndex: "start_endpoint",
          flex: 1,
          renderer: NOC.render.Lookup("start_endpoint"),
        },
        {
          text: __("End"),
          dataIndex: "end_endpoint",
          flex: 1,
          renderer: NOC.render.Lookup("end_endpoint"),
        },
        {
          text: __("Controller"),
          dataIndex: "controller",
          width: 150,
        },
        {
          text: __("Status"),
          dataIndex: "status",
          width: 50,
          renderer: function(v){
            return {
              "new": "<i class='fa fa-plus' style='color:" + NOC.colors.emerald + "' title='New'></i>",
              "done": "<i class='fa fa-check' style='color:" + NOC.colors.yes + "' title='Done'></i>",
              "broken": "<i class='fa fa-exclamation-triangle' style='color:" + NOC.colors.no + "' title='Broken'></i>",
            }[v];
          },
        },
      ],
      selModel: {
        selType: "rowmodel",
        listeners: {
          selectionchange: "onSelectionChange",
          deselect: "onDeselectChange",
        },
      } },
  ],
  onSelectionChange: function(selModel, selections){
    if(selections.length > 0){
      var isNew = Ext.isEmpty(selections[0].get("channel_id")),
        title = isNew ? __("Create new channel") : __("Update channel") + " " + selections[0].get("channel_name");
      this.fireEvent("magicselectionchange", false, isNew ? __("Create") : __("Update"), title);
    }
  },
  onDeselectChange: function(){
    this.fireEvent("magicselectionchange", true, __("Create"), __("Create new channel"));
  },
});