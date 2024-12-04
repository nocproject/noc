//---------------------------------------------------------------------
// Managed object inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.ManagedObjectInspector");

Ext.define("NOC.inv.map.inspectors.ManagedObjectInspector", {
  extend: "NOC.inv.map.inspectors.Inspector",
  title: __("Object Inspector"),
  inspectorName: "managedobject",

  tpl: [
    "<b>Name:</b>&nbsp;{[Ext.htmlEncode(values.name)]}<br/>",
    "<b>Address:</b>&nbsp;{address}<br/>",
    "<b>Profile:</b>&nbsp;{[Ext.htmlEncode(values.profile)]}<br/>",
    '<tpl if="platform">',
    "<b>Platform:</b>&nbsp;{[Ext.htmlEncode(values.platform)]}<br/>",
    "</tpl>",
    '<tpl if="external">',
    "<b>Segment:</b>&nbsp;{[Ext.htmlEncode(values.external_segment.name)]}<br/>",
    "</tpl>",
    '<tpl if="description">',
    "<b>Description:</b>&nbsp;{[Ext.htmlEncode(values.description)]}<br/>",
    "</tpl>",
  ],

  initComponent: function(){
    this.lookButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.pencil,
      scope: this,
      tooltip: __("Object settings"),
      handler: this.onLook,
      disabled: true,
    });

    this.cardButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.eye,
      scope: this,
      tooltip: __("View card"),
      handler: this.onMOCard,
      disabled: true,
    });

    this.segmentButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.location_arrow,
      scope: this,
      tooltip: __("Jump to Segment"),
      handler: this.onJumpSegment,
      disabled: true,
    });

    this.dashboardButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.line_chart,
      scope: this,
      tooltip: __("Show dashboard"),
      handler: this.onDashboard,
      disabled: true,
    });

    this.consoleButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.terminal,
      scope: this,
      tooltip: __("Console"),
      handler: this.onConsole,
      disabled: true,
    });

    this.viewMapButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.globe,
      scope: this,
      tooltip: __("Topology Neighbors"),
      handler: this.onNeighborsMap,
      disabled: true,
    });

    Ext.apply(this, {
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          this.cardButton,
          this.lookButton,
          this.viewMapButton,
          this.segmentButton,
          this.dashboardButton,
          this.consoleButton,
        ],
      }],
    });
    this.callParent();
  },

  onLook: function(){
    if(this.currentObjectId){
      NOC.launch("sa.managedobject", "history", {args: [this.currentObjectId]});
    }
  },

  onJumpSegment: function(){
    this.app.generator = this.app.mapPanel.objectNodes[this.currentObjectId].attributes.data.portal.generator;
    this.app.segmentCombo.restoreById(this.app.mapPanel.objectNodes[this.currentObjectId].attributes.data.portal.id);
  },

  onMOCard: function(){
    if(this.currentObjectId){
      window.open(
        "/api/card/view/managedobject/" + this.currentObjectId + "/",
      );
    }
  },

  onDashboard: function(){
    if(this.currentObjectId){
      window.open(
        "/ui/grafana/dashboard/script/noc.js?dashboard=mo&id=" + this.currentObjectId,
      );
    }
  },

  onConsole: function(){
    window.open(this.consoleUrl);
  },

  onNeighborsMap: function(){
    if(this.currentObjectId){
      NOC.launch("inv.map", "history", {
        args: ["objectlevelneighbor", this.currentObjectId, this.currentObjectId ],
      });
    }    
  },
  
  enableButtons: function(data){
    this.lookButton.setDisabled(false);
    this.cardButton.setDisabled(false);
    this.dashboardButton.setDisabled(false);
    this.consoleButton.setDisabled(false);
    this.viewMapButton.setDisabled(false);

    this.currentObjectId = data.id;
    this.consoleUrl = data.console_url;

    if(data.external){
      this.externalSegmentId = data.external_segment.id;
      this.segmentButton.setDisabled(false);
    } else{
      this.externalSegmentId = null;
      this.segmentButton.setDisabled(true);
    }
  },

  getDataURL: function(segmentId, objectId){
    var me = this,
      url = me.callParent([segmentId, objectId]);
    return url + objectId + "/";
  },
});
