//---------------------------------------------------------------------
// core.comboBox widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ComboBox");

Ext.define("NOC.core.ComboBox", {
  extend: "Ext.form.field.ComboBox",
  alias: "widget.core.combo",
  requires: [
    "NOC.core.Observable",
  ],
  displayField: "label",
  valueField: "id",
  queryMode: "remote",
  queryParam: "__query",
  queryCaching: false,
  queryDelay: 200,
  forceSelection: false,
  minChars: 2,
  typeAhead: true,
  triggerAction: "all",
  stateful: false,
  autoSelect: false,
  pageSize: true,
  width: "100%",
  listConfig: {
    minWidth: 240,
  },
  triggers: {
    clear: {
      cls: "x-form-clear-trigger",
      hidden: true,
      weight: -1,
      handler: function(field){
        field.setValue(null);
        field.fireEvent("select", field);
      },
    },
    create: {
      cls: "x-form-plus-trigger",
      hidden: true,
      handler: function(){
        NOC.launch(this.app, "new", {});
      },
    },
    update: {
      cls: "x-form-edit-trigger",
      hidden: true,
      handler: function(field){
        NOC.launch(this.app, "history", {args: [field.getValue()]});
      },
    },
  },
  listeners: {
    change: function(field, value){
      this.showTriggers(value);
    },
  },
  // custom properties
  isLookupField: true,
  restUrl: null,
  askPermission: true,
  hideTriggerUpdate: false,
  hideTriggerCreate: false,
  query: {},

  initComponent: function(){
    var tokens,
      extraParams = {"__format": "ext"};

    // Calculate restUrl
    if(Ext.isFunction(this.restUrl)){
      this.restUrl = this.restUrl();
    }

    if(!this.restUrl
            && Ext.String.startsWith(this.$className, "NOC.")
            && Ext.String.endsWith(this.$className, "LookupField")){
      this.restUrl = this.$className
                .replace("NOC", "")
                .replace(/\./g, "/")
                .replace("/LookupField", "/lookup/");
    }

    if(this.restUrl){
      tokens = this.restUrl.split("/");
      this.app = tokens[1] + "." + tokens[2];
    }
    // Fix combobox with paging
    this.pickerId = this.getId() + "_picker";
    // end
    this.showTriggers(null);
    if(!Ext.Object.isEmpty(this.query)){
      Ext.apply(extraParams, this.query);
    }
    Ext.apply(this, {
      store: {
        fields: ["id", "label"],
        pageSize: 25,
        proxy: {
          type: "rest",
          url: this.restUrl,
          pageParam: "__page",
          startParam: "__start",
          limitParam: "__limit",
          sortParam: "__sort",
          extraParams: extraParams,
          reader: {
            type: "json",
            rootProperty: "data",
            totalProperty: "total",
            successProperty: "success",
          },
        },
      },
    });
    this.callParent();
  },

  process: function(value, perms){
    this.getTrigger("create").hide();
    this.getTrigger("clear").show();
    if(value == null || value === ""){
      if(Ext.Array.contains(perms, "create")){
        if(!this.hideTriggerCreate) this.getTrigger("create").show();
      }
      this.getTrigger("clear").hide();
      this.getTrigger("update").hide();
      return;
    }
    if(Ext.Array.contains(perms, "launch")){
      if(!this.hideTriggerUpdate) this.getTrigger("update").show();
    }
  },

  showTriggers: function(value){
    if(this.askPermission){
      if(NOC.permissions$.isLoaded()){
        this.process(value, NOC.permissions$.getPermissions(this.app));
      } else{
        NOC.permissions$.subscribe({
          key: this.app,
          value: (perms) =>{
            this.process(value, perms);
          },
        },
        );
      }
    } else{
      this.process(value, []);
    }
  },

  getLookupData: function(){
    return this.getDisplayValue();
  },

  onSpecialKey: function(field, e){
    switch(e.keyCode){
      case e.ESC:
        this.clearValue();
        this.fireEvent("clear");
        break;
    }
  },

  onBeforeQuery: function(){
    var v = this.getRawValue();
    if(typeof v === "undefined" || v === null || v === ""){
      this.clearValue();
      this.fireEvent("clear");
    }
  },

  setValue: function(value, doSelect){
    var vm, params = {};

    if(value === null){
      this.callParent([value]);
      return;
    }
    if(typeof value === "string" || typeof value === "number"){
      if(value === "" || value === 0){
        this.clearValue();
        return;
      }
      params[this.valueField] = value;
      Ext.Ajax.request({
        url: this.restUrl,
        method: "GET",
        scope: this,
        params: params,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data.length === 1){
            vm = this.store.getModel().create(data[0]);
            this.setValue(vm);
            if(doSelect){
              this.fireEvent("select", this, vm, {});
            }
          }
        },
      });
    } else{
      if(!Ext.isDefined(value.data)){
        value = Ext.create("Ext.data.Model", value);
      }
      this.callParent([value]);
    }
  },
  // Called by ModelApplication
  cleanValue: function(record){
    var rv = record.get(this.name),
      mv = {};
    if(!rv || rv === "" || rv === 0){
      return ""
    }
    mv[this.valueField] = rv;
    mv[this.displayField] = record.get(this.name + "__label");
    if(mv[this.displayField] === undefined){
      // Incomplete input data. Just use value as label
      mv[this.displayField] = rv
    }
    return this.store.getModel().create(mv)
  },
});
