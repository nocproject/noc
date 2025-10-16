//---------------------------------------------------------------------
// Portal inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.ObjectPortalInspector");

Ext.define("NOC.inv.map.inspectors.ObjectPortalInspector", {
  extend: "NOC.inv.map.inspectors.Inspector",
  title: __("Portal Inspector"),
  inspectorName: "objectportal",

  tpl: [
    "<b>Name:</b>&nbsp;{[Ext.htmlEncode(values.name)]}<br/>",
    '<tpl if="description">',
    "<b>Description:</b>&nbsp;{[Ext.htmlEncode(values.description)]}<br/>",
    "</tpl>",
  ],

  initComponent: function(){

    this.portalButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.location_arrow,
      scope: this,
      tooltip: __("Jump to Portal"),
      handler: this.onJumpPortal,
      disabled: true,
    });

    Ext.apply(this, {
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          this.portalButton,
        ],
      }],
    });
    this.callParent();
  },

  onJumpPortal: function(){
    // this.app.generator = "segment";
    this.app.generator = this.gen_type;
    this.app.segmentCombo.restoreById(this.gen_id);
  },

  enableButtons: function(data){
    var me = this;

    me.gen_type = data.generator;
    me.gen_id = data.id;

    this.portalButton.setDisabled(false);
  },

  getDataURL: function(segmentId, objectId){
    var me = this,
      url = me.callParent([segmentId, objectId]);
    return url + objectId + "/";
  },

  preview: function(segmentId, data){

    this.update(data);
    this.enableButtons(data);
  },

});
