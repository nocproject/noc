//---------------------------------------------------------------------
// fm.event application inspector panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.EventInspector");

Ext.define("NOC.fm.event.EventInspector", {
  extend: "Ext.form.Panel",
  title: __("Event Inspector"),
  scrollable: true,
  bodyPadding: 4,
  defaultListenerScope: true,
  viewModel: {
    data: {
      id: null,
      message: null,
      snmp_trap_oid: null,
      labels: null,
      event_class: null,
      remote: null,
      target: null,
      object: null,
      segment: null,
      vars: null,
    },
    stores: {
      varsStore: {
        fields: ["name", "value", "type"],
        groupField: "type",
        sorters: ["type", "name"],
      },
    },
  },
  items: [
    {
      xtype: "displayfield",
      fieldLabel: __("ID"),
      bind: "{id}",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("Message"),
      bind: "{message}",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("TrapID"),
      bind: "{snmp_trap_oid}",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("Labels"),
      bind: "{labels}",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("Class"),
      bind: "{event_class}",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("Remote"),
      bind: "{remote}",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("Target"),
      bind: "{target}",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("Object"),
      bind: "{object}",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("Segment"),
      bind: "{segment}",
    },
    {
      xtype: "gridpanel",
      hideHeaders: true,
      forceFit: true,
      columnWidth: 1,
      features: [{
        ftype: "grouping",
        groupHeaderTpl: "{name}",
        collapsible: true,
        enableGroupingMenu: false,
      }],
      viewConfig: {
        stripeRows: true,
        enableTextSelection: true,
      },
      bind: {
        store: "{varsStore}",
      },
      columns: {
        defaults: {
          flex: 1,
          cellWrap: true,
          tdCls: "noc-white-space",
          renderer: function(value){
            return Ext.String.htmlEncode(value);
          },
        },
        items: [
          {dataIndex: "name"},
          {dataIndex: "value"},
        ],
      },
    },
  ],
  dockedItems: [
    {
      xtype: "toolbar",
      dock: "top",
      items: [
        {xtype: "button", text: "JSON", flex: 1, handler: "onJSON"},
        {xtype: "button", text: __("Reclassify"), flex: 1, handler: "onReclassify"},
      ],
    },
    {
      xtype: "toolbar",
      dock: "top",
      items: [
        {xtype: "button", text: __("Create Rule"), flex: 1, handler: "onCreateRule"},
        {xtype: "button", text: __("Create Ignore"), flex: 1, handler: "onCreateIgnorePattern"},
      ],
    },
  ],
  
  onJSON: function(){
    var app = this.up("[appId=fm.event]");
    app.showItem(app.ITEM_JSON);
    app.jsonPanel.preview({
      data: this.getViewModel().get("record"),
    });
  },
  //
  onReclassify: function(){
    Ext.Ajax.request({
      url: "/fm/event/" + this.getViewModel().data.id + "/reclassify/",
      method: "POST",
      success: function(){
        NOC.info(__("Event reclassified"));
      },
      failure: function(){
        NOC.error(__("Failed to reclassify"));
      },
    });
  },
  //
  onCreateRule: function(){
    var showGrid = function(){
      this.up().close();
    };
    NOC.launch("fm.classificationrule", "from_event", {
      "args": this.getViewModel().get("record"),
      "override": [
        {"showGrid": showGrid},
      ],
    });
  },

  onCreateIgnorePattern: function(){
    var showGrid = function(){
      this.up().close();
    };
    NOC.launch("fm.ignorepattern", "from_event", {
      "args": this.getViewModel().get("record"),
      "override": [
        {"showGrid": showGrid},
      ],
    }); 
  },
  //
  setRecord: function(record){
    if(Ext.Object.isEmpty(record)){
      return;
    }
    var object = record.get("object") || {},
      objectStr = Ext.Object.isEmpty(object) ? "-" : Ext.String.format("{0}({1})", object.name || "", object.address || ""),
      remoteStr = Ext.isEmpty(record.get("remote_system")) ? "-" : Ext.String.format("{0}:{1}", record.get("remote_system"), record.get("remote_id")),
      labels = Ext.isEmpty(record.get("labels")) ? "-" : NOC.render.LabelField(record.get("labels")),
      varsData = [...this.makeVarsData(__("Raw vars"), record.get("raw_vars")),
                  ...this.makeVarsData(__("Vars"), record.get("vars"))];
   
    this.getViewModel().set("record", record);
    this.getViewModel().setData({
      id: record.get("id") || "-",
      message: record.get("message") || "-",
      snmp_trap_oid: record.get("snmp_trap_oid") || "-",
      labels: labels,
      event_class: record.get("event_class") || "-",
      remote: remoteStr,
      target: Ext.String.format("{0}({1})", record.get("target") || "-", record.get("address") || "-"),
      object: objectStr,
      segment: record.get("segment") || "",
    });
    this.getViewModel().getStore("varsStore").loadData(varsData);
  },
  //
  makeVarsData: function(type, object){
    if(Ext.Object.isEmpty(object)){
      return [];
    }
    var data = [];
    Ext.Object.each(object, function(key, value){
      data.push({
        type: type,
        name: key,
        value: Ext.isObject(value) ? Ext.JSON.encode(value) : value,
      });
    });
    return data;
  },
});