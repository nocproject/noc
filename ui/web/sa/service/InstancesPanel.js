//---------------------------------------------------------------------
// sa.service InstancePanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.InstancesPanel");

Ext.define("NOC.sa.service.InstancesPanel", {
  extend: "NOC.core.ApplicationPanel",
  reference: "saInstancesPanel",
  alias: "widget.sa.instances",
  requires: [
    "NOC.sa.service.InstanceModel",
    "NOC.sa.service.ManagedObjectLinkForm",
    "NOC.sa.service.ResourceLinkForm",
    "NOC.sa.service.AddressesLinkForm",
    "NOC.sa.service.RegisterForm",
    "Ext.ux.form.SearchField",
  ],
  layout: "fit",
  defaultListenerScope: true,
  viewModel: {
    stores: {
      sourceStore: {
        fields: ["id", "label"],
        data: [
          {id: "M", label: __("Manual")},
          {id: "D", label: __("Discovery")},
          {id: "E", label: __("ETL")},
        ],
      },
      typeStore: {
        fields: ["id", "label"],
        data: [
          {id: "network", label: __("Network")},
          {id: "endpoint", label: __("Endpoint")},
          {id: "other", label: __("Other")},
        ],
      },
      gridStore: {
        model: "NOC.sa.service.InstanceModel",
        filters: [
          {
            property: "name",
            value: "{searchText}",
            anyMatch: true,
            caseSensitive: false,
          },
        ],
      },
    },
    data: {
      searchText: "",
      record: undefined,
      showOnClose: "ITEM_FORM",
      enableRegisterBtn: false,
      enableUnregisterBtn: false,
      selectedInstance: null,
    },
    formulas: {
      canUnregister: function(get){
        return get("enableUnregisterBtn") && get("selectedInstance") !== null;
      },
    },
  },
  tbar: [
    {
      text: __("Close"),
      tooltip: __("Close without saving"),
      glyph: NOC.glyph.arrow_left,
      handler: "onClose",
    },
    "|",
    {
      xtype: "searchfield",
      triggers: {
        clear: {
          cls: "x-form-clear-trigger",
          hidden: true,
          handler: function(field){
            field.setValue(null);
          },
        },
      },
      listeners: {
        change: function(field, value){
          if(value == null || value === ""){
            this.getTrigger("clear").hide();
            return;
          }
          this.getTrigger("clear").show();
        },
      },
      bind: {value: "{searchText}"},
    },

    "|",
    {
      text: __("Register"),
      bind: {
        disabled: "{!enableRegisterBtn}",
      },
      handler: "open_registerForm",
    },
    {
      text: __("Unregister"),
      bind: {
        disabled: "{!canUnregister}",
      },
      handler: "onUnregister",
    },
  ],
  items: [
    {
      xtype: "gridpanel",
      reference: "instancesGrid",
      scrollable: true,
      forceFit: true,
      sortableColumns: false,
      bind: {
        store: "{gridStore}",
        selection: "{selectedInstance}",
      },
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          editor: "textfield",
          renderer: "lockIcon",
        },
        {
          text: __("FQDN"),
          editor: "textfield",
          dataIndex: "fqdn",
        },
        {
          text: __("Port"),
          maxWidth: 100,
          editor: {
            xtype: "numberfield",
            minValue: 0,
            maxValue: 65535,
          },
          dataIndex: "port",
        },
        {
          text: __("Sources"),
          dataIndex: "sources",
          maxWidth: 120,
          renderer: function(value){
            var app = this.up("[reference=saInstancesPanel]");
            return app.renderStoreValue("sourceStore", value.split(","));
          },
        },
        {
          text: __("Type"),
          dataIndex: "type",
          maxWidth: 120,
          renderer: function(value){
            var app = this.up("[reference=saInstancesPanel]");
            return app.renderStoreValue("typeStore", value.split(","));
          },
        },
        {
          text: __("Managed Object"),
          dataIndex: "managed_object",
          renderer: function(value, meta, record){
            var v = value ? record.get("managed_object__label") : "...",
              app = this.up("[reference=saInstancesPanel]");
            return app.renderLink(v, record);
          },
          // invoke open_managed_objectForm
          onClick: "openForm",
        },
        {
          text: __("Addresses"),
          dataIndex: "addresses",
          renderer: function(value, meta, record){
            var app = this.up("[reference=saInstancesPanel]");
            return app.renderLink(app.renderArrayValue(value, "address"), record);
          },
          // invoke open_addressesForm
          onClick: "openForm",
        },
        {
          text: __("Resources"),
          dataIndex: "resources",
          renderer: function(value, meta, record){
            var app = this.up("[reference=saInstancesPanel]");
            return app.renderLink(app.renderArrayValue(value, "resource__label"), record);
          },
          // invoke open_resourcesForm
          onClick: "openForm",
        },
      ],
      viewConfig: {
        listeners: {
          cellclick: "onCellClick",
          beforecellclick: "onBeforeCellClick",
        },
      },
      plugins: [
        {
          ptype: "rowediting",
          clicksToEdit: 1,
          listeners: {
            beforeedit: "checkEditing",
            edit: "updateInstance",
          },
        },
      ],
    },
  ],
  onCellClick: function(view, cell, cellIndex, record, row, rowIndex, e){
    if(e.target.tagName === "A"){
      var column = view.panel.headerCt.getHeaderAtIndex(cellIndex);
      if(column.onClick){
        this["open_" + column.dataIndex + "Form"].apply(this, [record]);
      }
    }
  },
  onBeforeCellClick: function(view, td, cellIndex, record, row, rowIndex, e){
    var sm = view.getSelectionModel(),
      column = view.headerCt.getHeaderAtIndex(cellIndex);
    if(sm.isSelected(record)){
      if(e.target.tagName === "A"
        && ["addresses", "resources", "managed_object"].includes(column.dataIndex)){
        return true;
      }
      if(["name", "fqdn", "port"].includes(column.dataIndex)){
        return true;
      }
      sm.deselectAll();
      return false;
    }
  },
  renderLink: function(value, record){
    var allow_update = record.get("allow_update");
    if(allow_update){
      return "<a href='javascript:void(0);' class='noc-clickable-cell' title='Click to change...'>" + value + "</a>";
    }
    return value;
  },
  renderArrayValue: function(value, label){
    if(Ext.isEmpty(value)) return "..."
    if(Ext.isArray(value)) return value.map(el => el[label]).join(", ");
    return value[label];
    
  },
  renderStoreValue: function(storeName, value){
    var store = this.lookupViewModel().getStore(storeName),
      getLabel = function(id){ return store.getById(id).get("label"); };
    
    if(Ext.isEmpty(value)) return "-";
    if(Ext.isArray(value)) return value.map(el => getLabel(el)).join(", ");
    return getLabel(value);
  },
  onClose: function(){
    var app = this.up("[appId=sa.service]"),
      showOnClose = this.getViewModel().get("showOnClose");
    if(showOnClose === "ITEM_GRID") Ext.History.setHash("sa.service");
    app.showItem(app[showOnClose]);
  },
  load: function(record, showOnClose){
    var vm = this.getViewModel();
    vm.set("record", record);
    vm.set("showOnClose", showOnClose);
    vm.set("enableRegisterBtn", this.up().hasPermission("register_instance"));
    vm.set("enableUnregisterBtn", this.up().hasPermission("unregister_instance"));
    this.mask(__("Loading instances..."));
    Ext.Ajax.request({
      url: "/sa/service/" + record.id + "/instance/",
      method: "GET",
      scope: this,
      success: function(response){
        let data = Ext.decode(response.responseText);
        this.getViewModel().getStore("gridStore").loadData(data);
        NOC.info(__("Instances loaded"));
      },
      failure: function(response){
        var text = Ext.decode(response.responseText); 
        NOC.error(text.message || __("Failed to load instances"));
      },
      callback: function(){
        this.unmask();
      },
    });
  },
  open_managed_objectForm: function(record){
    var name = record.get("managed_object__label"),
      isNewLink = Ext.isEmpty(record.get("managed_object")),
      title = __("Update/Unlink") + " " + name,
      service = this.getViewModel().get("record");
    if(isNewLink){
      title = __("Link Managed Object");
    }
    var form = Ext.create("NOC.sa.service.ManagedObjectLinkForm", {
      title: title,
    });
    form.down("form").getForm().setValues({
      managed_id: record.get("managed_object"),
      service_id: service.id,
      instance_id: record.id,
    });
    form.instanceRecord = record;
  },
  open_addressesForm: function(record){
    var service = this.getViewModel().get("record"), 
      form = Ext.create("NOC.sa.service.AddressesLinkForm", {
        title: __("Bind Addresses"),
      });
    form.down("form").getForm().setValues({
      service_id: service.id,
      instance_id: record.id,
    });
    form.restoreRows(record.get("addresses"));
    form.instanceRecord = record;
  },
  open_resourcesForm: function(record){
    var service = this.getViewModel().get("record"),
      resourceUrl = "/sa/service/" + service.id + "/resource/interface/",
      form = Ext.create("NOC.sa.service.ResourceLinkForm", {
        title: __("Interface <Bind>"),
      }),
      managed_id = record.get("managed_object"),
      resources = record.get("resources"),
      resourceCombo = form.down("[name=resources]"),
      resourceComboProxy = resourceCombo.getStore().getProxy();
    if(!Ext.isEmpty(resources)){
      managed_id = resources[0].managed_object;
    }
    form.down("form").getForm().setValues({
      managed_id: managed_id,
      service_id: service.id,
      instance_id: record.id,
    });
    resourceComboProxy.setUrl(resourceUrl);
    if(!Ext.isEmpty(managed_id)){
      resourceComboProxy.setExtraParams({
        managed_object: managed_id,
      });
      if(!Ext.isEmpty(resources)) resourceCombo.setValue({resource: resources[0].resource, resource__label: resources[0].resource__label});
    }
    form.instanceRecord = record;
  },
  open_registerForm: function(){
    var service = this.getViewModel().get("record"),
      form = Ext.create("NOC.sa.service.RegisterForm");
    form.down("form").getForm().setValues({
      service_id: service.id,
    });
    form.down("form [name=type]").setStore(this.getViewModel().getStore("typeStore"));
    form.instanceStore = this.getViewModel().getStore("gridStore");
  },
  lockIcon: function(value, meta, record){
    var icon = "<i class='fa fa-lock' style='padding-right: 4px;' title='" + __("Row read only") + "'></i>";
    if(record.get("allow_update")){
      return value;
    }
    return icon + value;
  },
  checkEditing: function(editor, context){
    if(!context.record.get("allow_update")){
      context.cancel = true;
      return;
    }
    if(["fqdn", "port", "name"].includes(context.column.dataIndex)){ 
      context.cancel = false;
      return;
    }
    context.cancel = true;
  },
  updateInstance: function(editor, context){
    var params = {}, record = context.record,
      serviceId = this.getViewModel().get("record").id,
      url = "/sa/service/" + serviceId + "/instance/" + record.id + "/";
    if(!Ext.isEmpty(record.get("name"))){
      params["name"] = record.get("name"); 
    }
    if(!Ext.isEmpty(record.get("fqdn"))){
      params["fqdn"] = record.get("fqdn"); 
    }
    if(!Ext.isEmpty(record.get("port"))){
      params["port"] = record.get("port"); 
    }
    context.record.commit();
    this.request(url, params, context.record);
  },
  request: function(url, params, record){
    Ext.Ajax.request({
      url: url,
      method: "PUT",
      scope: this,
      jsonData: params,
      success: function(response){
        var result = Ext.decode(response.responseText);
        if(result.success){
          NOC.info(__("Instance updated successfully"));
          record.set("name", result.data.name);
          record.set("fqdn", result.data.fqdn);
          record.set("port", result.data.port);
        } else{
          NOC.error(__("Error") + ": " + (result.message || __("Failed to update instance")));
        }
      },
      failure: function(response){
        var result = Ext.decode(response.responseText);
        NOC.error(__("Error") + ": " + (result.errors || __("Server error occurred")));
      },
    });
  },
  onUnregister: function(){
    var vm = this.getViewModel(),
      serviceId = vm.get("record").id,
      instanceId = vm.get("selectedInstance").id,
      url = "/sa/service/" + serviceId + "/unregister_instance/" + instanceId + "/";
    
    Ext.Ajax.request({
      url: url,
      method: "POST",
      scope: this,
      success: function(response){
        var result = Ext.decode(response.responseText);
        if(result.success){
          NOC.info("Instance unregister successfully");
          this.reloadInstanceStore(serviceId);
        } else{
          NOC.error("Error " + " : " + result.message || "Operation failed");
        }
      },
      failure: function(response){
        var result = Ext.decode(response.responseText);
        NOC.error("Error " + " : " + result.message || "Server error occurred");
      },
    });
  },
  reloadInstanceStore: function(serviceId){
    Ext.Ajax.request({
      url: "/sa/service/" + serviceId + "/instance/",
      method: "GET",
      scope: this,
      success: function(response){
        let data = Ext.decode(response.responseText);
        this.getViewModel().getStore("gridStore").loadData(data);
      },
      failure: function(response){
        var text = Ext.decode(response.responseText);
        NOC.error(text.message || __("Failed to load instances"));
      },
      callback: function(){
        this.unmask();
      },
    });
  },
});
