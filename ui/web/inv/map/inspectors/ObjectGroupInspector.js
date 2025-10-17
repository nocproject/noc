//---------------------------------------------------------------------
// Managed object inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.ObjectGroupInspector");

Ext.define("NOC.inv.map.inspectors.ObjectGroupInspector", {
  extend: "NOC.inv.map.inspectors.Inspector",
  title: __("ObjectGroup Inspector"),
  inspectorName: "objectgroup",

  tpl: [
    "<b>Name:</b>&nbsp;{[Ext.htmlEncode(values.name)]}<br/>",
    '<tpl if="description">',
    "<b>Description:</b>&nbsp;{[Ext.htmlEncode(values.description)]}<br/>",
    "</tpl>",
  ],

  initComponent: function(){

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
      tooltip: __("Jump to Group"),
      handler: this.onJumpSegment,
      disabled: true,
    });

    Ext.apply(this, {
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          this.cardButton,
          this.segmentButton,
        ],
      }],
    });
    this.callParent();
  },

  onJumpSegment: function(){
    this.app.generator = "objectgroup";
    this.app.segmentCombo.restoreById(this.currentObjectId);
  },

  onMOCard: function(){
    if(this.currentObjectId){
      window.open(
        "/api/card/view/resourcegroup/" + this.currentObjectId + "/",
      );
    }
  },


  enableButtons: function(data){
    this.cardButton.setDisabled(false);
    this.segmentButton.setDisabled(false);
    this.currentObjectId = data.id;
  },

  getDataURL: function(segmentId, objectId){
    var me = this,
      url = me.callParent([segmentId, objectId]);
    return url + objectId + "/";
  },
});
