//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.controller.Sidebar");

Ext.define("NOC.sa.discoveredobject.controller.Sidebar", {
  extend: "Ext.app.ViewController",
  alias: "controller.sa.discoveredobject.sidebar",

  init: function(){
    this.reloadTask = new Ext.util.DelayedTask(this.reload, this);
  },
  setFilter: function(field, event){
    var value = field.getValue();

    if(!field.isValid()){
      return
    }
    if(field.name && "addresses" === field.name){
      value = value.split("\n")
                .filter(function(ip){
                  return ip.length > 0;
                })
                .map(function(ip){
                  return ip.trim();
                });

      if(value.length > 2000){
        NOC.msg.failed(__("Too many IP, max 2000"));
        return;
      }
    }

    if("Ext.event.Event" === Ext.getClassName(event)){
      if(Ext.EventObject.ENTER === event.getKey()){
        this.reloadData();
      }
      return;
    }

    this.reloadData();
  },
  reloadData: function(){
    var appView = this.view.up("[appId]"),
      filterObject = this.getView().getForm().getValues();

    Ext.Object.each(filterObject, function(key, value){
      if(value == null || value === ""){
        delete filterObject[key];
      }
    });

    this.getView().setValue(filterObject);

    // don't save parameter 'addresses' into url
    var queryObject = Ext.clone(filterObject);
    if(queryObject.hasOwnProperty("addresses")){
      delete queryObject["addresses"];
    }

    var token = "", query = Ext.Object.toQueryString(queryObject, true);

    if(query.length > 0){
      token = "?" + query;
    }

    Ext.History.add(appView.appId + token, true);

    this.reloadTask.cancel();
    this.reloadTask.delay(500);
  },
  reload: function(){
    var appView = this.view.up("[appId]"),
      filterObject = this.notEmptyValues(),
      grid = appView.down("grid"),
      store = grid.getStore();

    grid.mask(__("Loading..."));
    store.getProxy().setExtraParams(filterObject);
    store.load({
      callback: function(){
        grid.unmask();
      },
    });
  },
  restoreFilter: function(){
    var queryStr = Ext.util.History.getToken().split("?")[1];

    if(queryStr){
      var params = Ext.Object.fromQueryString(queryStr, true),
        view = this.getView();

      view.down("form").getForm().setValues(params);
      view.setValue(params);
      view.fireEvent("filterChanged", this.getView(), params);
    }
  },
  cleanAllFilters: function(button){
    var appView = this.view.up("[appId]");

    Ext.History.add(appView.appId);
    button.up("form").getForm().reset();
    this.getView().fireEvent("filterChanged", this.getView(), {});
    this.reloadData();
  },
  notEmptyValues: function(){
    var cloned = Ext.clone(this.getView().getForm().getValues());

    Ext.Object.each(cloned, function(key, value){
      if(Ext.isEmpty(value)){
        delete cloned[key];
      }
    });

    return cloned;
  },
  onChange: Ext.emptyFn,
});
