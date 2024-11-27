//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.DurationFilterRowController");
Ext.define("NOC.fm.alarm.view.grids.FavoriteStatusGroup", {
  extend: "Ext.container.Container",
  alias: "widget.fm.alarm.fav.status",
  itemId: "fav_status",
    
  layout: {
    type: "hbox",
  },
    
  config: {
    value: null,
  },
    
  publishes: ["value"],
  twoWayBindable: ["value"],
    
  items: [ {
    xtype: "displayfield",
    fieldLabel: __("Favorites"),
    allowBlank: true,
    flex: 2,
  },{
    xtype: "button",
    itemId: "favoriteBtn",
    glyph: NOC.glyph.star,
    cls: "noc-starred",
    enableToggle: true,
    // margin: "0 5 0 0",
    listeners: {
      toggle: function(btn, pressed){
        var me = this.up("#fav_status");
        if(pressed){
          me.setValue(true);
          me.down("#unfavoriteBtn").setPressed(false);
        } else if(!me.down("#unfavoriteBtn").pressed){
          me.setValue(null);
        }
      },
    },
  }, {
    xtype: "button",
    itemId: "unfavoriteBtn",
    glyph: NOC.glyph.star,
    cls: "noc-unstarred",
    enableToggle: true,
    listeners: {
      toggle: function(btn, pressed){
        var me = this.up("#fav_status");
        if(pressed){
          me.setValue(false);
          me.down("#favoriteBtn").setPressed(false);
        } else if(!me.down("#favoriteBtn").pressed){
          me.setValue(null);
        }
      },
    },
  }],
    
  updateValue: function(value){
    var favoriteBtn = this.down("#favoriteBtn"),
      unfavoriteBtn = this.down("#unfavoriteBtn");
      
    if(typeof value === "string"){
      value = value.toLowerCase() === "true";
    }        
    if(value === true){
      favoriteBtn.setPressed(true);
      unfavoriteBtn.setPressed(false);
    } else if(value === false){
      favoriteBtn.setPressed(false);
      unfavoriteBtn.setPressed(true);
    } else{
      favoriteBtn.setPressed(false);
      unfavoriteBtn.setPressed(false);
    }
  },
});