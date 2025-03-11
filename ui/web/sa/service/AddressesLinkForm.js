//---------------------------------------------------------------------
// Link Address window
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.AddressesLinkForm");

Ext.define("NOC.sa.service.AddressesLinkForm", {
  extend: "Ext.Window",
  requires: [
    "NOC.core.ComboBox",
  ],
  autoShow: true,
  closable: true,
  maximizable: true,
  modal: true,
  scrollable: true,
  layout: "fit",
  initComponent: function(){
    Ext.apply(this, {
      items: [{
        xtype: "form",
        padding: 4,
        width: 400,
        items: [
          {
            xtype: "hidden",
            name: "service_id",
            value: this.service_id,
          },
          {
            xtype: "hidden",
            name: "instance_id",
            value: this.instance_id,
          },
          {
            xtype: "container",
            itemId: "addresses-container",
            layout: {
              type: "vbox",
            },
          },
        ],
        buttons: [
          {
            text: __("Bind"),
            formBind: true,
            handler: this.buttonHandler("bind"),
          },
          {
            text: __("Unbind"),
            handler: this.buttonHandler("unbind"), 
          },
          {
            text: __("Reset"),
            scope: this,
            handler: this.resetFormHandler,
          },
          {
            text: __("Close"),
            handler: function(){
              this.up("window").close();
            }, 
          },
        ],
      }],
    });
    this.callParent();
    this.restoreRows(this.addresses);
  },
  getRowConfig: function(type){
    return {
      xtype: "container",
      layout: {
        type: "hbox",
        align: "end",
      },
      items: [
        this.getButtonConfig(type),
        this.getAddressTextConfig(),
        // this.getPoolComboConfig(),
      ],
    }    
  },
  getButtonConfig: function(type){
    var tooltip = type === "add" ? __("Add Input") : __("Remove Input"),
      glyph = type === "add" ? NOC.glyph.plus : NOC.glyph.minus,
      config = {
        xtype: "button",
        glyph: glyph,
        tooltip: tooltip,
        disabled: true,
      };
      
    if(type === "add"){
      config.handler = this.addRowButtonHandler;
    } else{
      config.disabled = false;
      config.handler = this.removeRow;
    }
    return config;
  },
  getAddressTextConfig: function(){
    return {
      xtype: "textfield",
      name: "address",
      allowBlank: false,
      emptyText: __("Address"),
      labelWidth: 150,
      regex: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
      regexText: __("Invalid IP address format"),
      listeners: {
        validitychange: function(field, isValid){
          var removeBtn = field.up().down("button");
          removeBtn.setDisabled(!isValid);
        },
      },
    };
  },
  getPoolComboConfig: function(){
    return {
      xtype: "core.combo",
      name: "pool",
      emptyText: __("Select Pool"),
      restUrl: "/main/pool/lookup/",
      uiStyle: "medium-combo",
    };
  },
  addRowButtonHandler: function(){
    var rowsContainer = this.up("form").down("[itemId=addresses-container]");
    rowsContainer.add(Ext.create(this.up("window").getRowConfig("remove")));
  },
  removeRow: function(button){
    var row = button.up(),
      rowsContainer = row.up();
    rowsContainer.remove(row);
  },
  restoreRows(rows){
    var addressesContainer = this.down("[itemId=addresses-container]");
    addressesContainer.removeAll();
    rows = Ext.isArray(rows) ? rows : [rows];
    if(Ext.isEmpty(rows)){ 
      addressesContainer.add(this.getRowConfig("add"));
      this.center();
      return;
    }
    Ext.each(rows, function(row, index){ 
      var rowComponent = addressesContainer.add(this.getRowConfig(index === 0 ? "add" : "remove"));
      this.setRowValues(rowComponent, row);
    }, this);
    this.center();
  },
  setRowValues: function(rowComponent, values){
    rowComponent.down("field[name=address]").setValue(values.address);
    // rowComponent.down("[name=pool]").setValue(values.pool);
  },
  buttonHandler: function(method){
    return function(){
      var form = this.up("window"),
        data = this.up("form").getForm().getValues(),
        isAddressArray = Ext.isArray(data.address),
        // pools =isAddressArray ? data.pool : [data.pool], 
        addresses = Ext.Array.map(
          isAddressArray ? data.address : [data.address],
          function(address){
            return {
              address: address,
              // pool: pools[index] || "",
            };
          }),
        url = "/sa/service/" + data.service_id
          + "/instance/" + data.instance_id + "/" + method + "/",
        params = {addresses: addresses};
      if(method === "unbind"){
        url += "addresses/";
        params = undefined;
      }
      form.request.call(form, url, params, method);
    };
  },
  request: function(url, params, method){
    Ext.Ajax.request({
      url: url,
      method: "PUT",
      jsonData: params,
      success: function(response){
        var result = Ext.decode(response.responseText);
        if(result.success){
          this.instanceRecord.set("addresses", result.data.addresses);
          this.instanceRecord.commit();
          NOC.info(__("Address") + " " + method + " " + __("successfully"));
          this.close();
        } else{
          NOC.error(__("Error") + " : " + result.message || __("Operation failed"));
        }
      },
      failure: function(){
        NOC.error("Error : Server error occurred");
      },
      scope: this,
    });
  },
  resetFormHandler: function(){
    var mappingContainer = this.down("[itemId=addresses-container]");
    mappingContainer.removeAll();
    mappingContainer.add(this.getRowConfig("add", true));
    this.down("form").getForm().reset();
    this.center();
  },
});