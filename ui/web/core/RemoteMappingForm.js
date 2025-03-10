//---------------------------------------------------------------------
// Remote Mapping Form 
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.RemoteMappingForm");

Ext.define("NOC.core.RemoteMappingForm", {
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
  title: __("Remote Mapping"),
  initComponent: function(){
    Ext.apply(this, {
      items: [{
        xtype: "form",
        padding: 4,
        items: [
          {
            xtype: "hidden",
            name: "managedobject_id",
            value: this.managedObjectId,
          },
          {
            xtype: "container",
            itemId: "mapping-container",
            layout: {
              type: "vbox",
            },
          },
        ],
        buttons: [
          {
            text: __("Map"),
            formBind: true,
            scope: this,
            handler: this.mappingHandler,
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
    this.restoreRows();
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
        {
          xtype: "core.combo",
          restUrl: "/main/remotesystem/lookup/",
          name: "remote_system",
          allowBlank: false,
          uiStyle: "medium-combo",
        },
        {
          xtype: "textfield",
          name: "remote_id",
          allowBlank: false,
          uiStyle: "medium",
        }],
    }    
  },
  getButtonConfig: function(type){
    var tooltip = type === "add" ? __("Add Mapping") : __("Remove Mapping"),
      glyph = type === "add" ? NOC.glyph.plus : NOC.glyph.minus,
      config = {
        xtype: "button",
        glyph: glyph,
        tooltip: tooltip,
        disabled: false,
      };
      
    if(type === "add"){
      config.handler = this.addRowButtonHandler;
    } else{
      config.handler = this.removeRow;
    }
    return config;
  },
  addRowButtonHandler: function(){
    var rowsContainer = this.up("form").down("[itemId=mapping-container]");
    rowsContainer.add(Ext.create(this.up("window").getRowConfig("remove", false)));
  },
  removeRow: function(button){
    var row = button.up(),
      rowsContainer = row.up();
    rowsContainer.remove(row);
  },
  restoreRows(){
    var mappingContainer = this.down("[itemId=mapping-container]"),
      rows = Ext.isArray(this.mappings) ? this.mappings : [this.mappings];
    mappingContainer.removeAll();
    if(Ext.isEmpty(rows)){ 
      mappingContainer.add(this.getRowConfig("add", true));
      this.center();
      return;
    }
    Ext.each(rows, function(row, index){ 
      var rowComponent = mappingContainer.add(this.getRowConfig(index === 0 ? "add" : "remove", false));
      this.setRowValues(rowComponent, row);
    }, this);
    this.center();
  },
  setRowValues: function(rowComponent, values){
    rowComponent.down("field[name=remote_system]").setValue(values.remote_system);
    rowComponent.down("field[name=remote_id]").setValue(values.remote_id);
  },
  mappingHandler: function(){
    var data = this.down("form").getForm().getValues(),
      url = "/sa/managedobject/" + data.managedobject_id + "/mappings/",
      isMappingsArray = Ext.isArray(data.remote_system),
      remote_ids = isMappingsArray ? data.remote_id : [data.remote_id],
      mappings = Ext.Array.map(
        isMappingsArray ? data.remote_system : [data.remote_system],
        function(remote_system, index){
          return {
            remote_system: remote_system,
            remote_id: remote_ids[index],
          };
        });
    this.request(url, {mappings: mappings});
  },
  request: function(url, params){
    Ext.Ajax.request({
      url: url,
      method: "POST",
      jsonData: params,
      success: function(response){
        var result = Ext.decode(response.responseText);
        if(result.status){
          this.parentForm.getForm().setValues({mappings: result.data});
          this.parentForm.currentRecord.set("mappings", result.data);
          NOC.info(__("Mapping was performed successfully"));
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
});