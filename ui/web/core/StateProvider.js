//---------------------------------------------------------------------
// NOC.core.StateProvider - REST State provider
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.StateProvider");

Ext.define("NOC.core.StateProvider", {
  extend: "Ext.state.Provider",
  url: "/main/desktop/state/",

  constructor: function(){
    var me = this;
    me.callParent();
    me.state = {};
  },

  loadState: async function(){
    try{
      const response = await fetch(this.url);
      if(response.ok){
        const states = await response.json();
        for(var k in states){
          states[k] = this.decodeValue(states[k])
        }
        this.state = states;
      }
    } catch(error){
      console.error("Error loading preferences:", error);
    }
  },

  get: function(name, defaultValue){
    var ret = this.state[name];
    return ret === undefined ? defaultValue : ret;
  },
  
  set: function(name, value){
    var me = this;
    me.callParent([name, value]);
    fetch(me.url + name + "/", {
      method: "POST",
      body: me.encodeValue(value),
    }).catch(error => console.error("Error saving state:", error));
  },

  clear: function(name){
    var me = this;
    me.callParent([name]);
    fetch(me.url + name + "/", {
      method: "DELETE",
    }).catch(error => console.error("Error clearing state:", error));
  },
});
