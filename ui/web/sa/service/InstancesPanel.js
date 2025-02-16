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
      showOnClose: "ITEM_FORM",
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
    },
    {
      text: __("Unregister"),
    },
  ],
  items: [
    {
      xtype: "gridpanel",
      reference: "instancesGrid",
      scrollable: true,
      forceFit: true,
      bind: {
        store: "{gridStore}",
      },
      columns: [
        {
          text: __("Sources"),
          dataIndex: "sources",
          renderer: function(value){
            var app = this.up("[reference=saInstancesPanel]");
            return app.renderStoreValue("sourceStore", value);
          },
        },
        {
          text: __("Type"),
          dataIndex: "type",
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
            return app.renderLink(v);
          },
          // invoke open_managed_objectForm
          onClick: "openForm",
        },
        {
          text: __("FQDN"),
          dataIndex: "fqdn",
        },
        {
          text: __("Port"),
          dataIndex: "port",
        },
        {
          text: __("Addresses"),
          dataIndex: "addresses",
          renderer: function(value){
            var app = this.up("[reference=saInstancesPanel]");
            return app.renderLink(app.renderArrayValue(value, "address"));
          },
          // invoke open_addressesForm
          onClick: "openForm",
        },
        {
          text: __("Name"),
          dataIndex: "name",
        },
        {
          text: __("Resources"),
          dataIndex: "resources",
          renderer: function(value){
            var app = this.up("[reference=saInstancesPanel]");
            return app.renderLink(app.renderArrayValue(value, "resource_label"));
          },
          // invoke open_resourcesForm
          onClick: "openForm",
        },
        {
          text: __("Allow"),
          dataIndex: "allow_update",
          renderer: NOC.render.Bool,
        },
      ],
      viewConfig: {
        listeners: {
          cellclick: "onCellClick",
        },
      },
    },
  ],
  onCellClick: function(view, cell, cellIndex, record, row, rowIndex, e){
    if(e.target.tagName === "A"){
      var header = view.panel.headerCt.getHeaderAtIndex(cellIndex);
      if(header.onClick){
        this["open_" + header.dataIndex + "Form"].apply(this, [record]);
      }
    }
  },
  renderLink: function(value){
    return "<a href='javascript:void(0);' class='noc-clickable-cell' title='Click to change...'>" + value + "</a>"; 
  },
  renderArrayValue: function(value, label){
    if(Ext.isEmpty(value)) return "...";
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
    this.getViewModel().set("record", record);
    this.getViewModel().set("showOnClose", showOnClose);
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
  },
  open_resourcesForm: function(record){
    var service = this.getViewModel().get("record"),
      resourceUrl = "/sa/service/" + service.id + "/resource/interface/",
      form = Ext.create("NOC.sa.service.ResourceLinkForm", {
        title: __("Interface <Bind>"),
      }),
      resourceComboProxy = form.down("[name=resources]").getStore().getProxy();
    form.down("form").getForm().setValues({
      managed_id: record.get("managed_object"),
      service_id: service.id,
      instance_id: record.id,
    });
    resourceComboProxy.setUrl(resourceUrl);
    if(!Ext.isEmpty(record.get("managed_object"))){
      resourceComboProxy.setExtraParams({
        managed_object: record.get("managed_object"),
      });
    }
  },
});
