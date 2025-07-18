//---------------------------------------------------------------------
// aaa.group Permissions widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.aaa.group.Permission");

Ext.define("NOC.aaa.group.Permission", {
  extend: "Ext.panel.Panel",
  mixins: [
    "Ext.form.field.Base",
  ],
  requires: [
    "NOC.aaa.group.ApplicationPermission",
  ],
  alias: "widget.noc.group.permission",
  defaultListenerScope: true,
  setValue: function(value){
    if(!Ext.isEmpty(value)){
      let data = this.unpack(value);
      this.removeAll(true);
      Ext.Object.each(data, function(name, module){
        var me = this;
        me.add({
          xtype: "noc.group.applicationperm",
          title: module.name + " (" + name + ")",
          data: module.apps,
          listeners: {
            afterrender: function(panel){
              panel.header.el.on("click", Ext.pass(panel.togglePanel, panel));
            },
          },
        });
      }, this);
    }
  },
  getValue: function(){
    var data = [];
    Ext.each(this.getRefItems(), function(panel){
      Ext.Object.each(panel.getData(), function(name, title){
        Ext.each(title.perms, function(p){
          if(p.status){
            data.push(p.id.replace(/-/g, ":"));
          }
        });
      });
    });
    return data;
  },
  resetAllPermission: function(){
    Ext.each(this.getRefItems(), function(panel){
      panel.resetPermission();
    });
  },
  isPacked: function(value){
    return typeof value === "object" && "name" in value;
  },
  unpack: function(value){
    var data = {};
    if(!this.isPacked(value[0])){
      return value;
    }
    Ext.each(value, function(val){
      var perms = val.name.split(":"),
        module = perms[0],
        app = perms[1],
        permission = perms[2],
        makeId = function(name){
          return name.replace(/:/g, "-");
        };
      if(module in data){
        if("apps" in data[module] && app in data[module]["apps"]){
          data[module]["apps"][app]["perms"].push({
            id: makeId(val.name),
            name: permission,
            status: val.status,
          });
        } else{
          // add application
          data[module]["apps"][app] = {title: val.title};
          data[module]["apps"][app]["perms"] = [{id: makeId(val.name), name: permission, status: val.status}];
        }
      } else{
        // add module
        data[module] = {name: val.module};
        data[module]["apps"] = {};
        data[module]["apps"][app] = {title: val.title};
        data[module]["apps"][app]["perms"] = [{id: makeId(val.name), name: permission, status: val.status}];
      }
    });
    return data;
  },
});