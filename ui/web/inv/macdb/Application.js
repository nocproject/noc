//---------------------------------------------------------------------
// inv.macdb application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.Application");

Ext.define("NOC.inv.macdb.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.inv.macdb.MACLogForm",
    "NOC.inv.macdb.Model",
    "NOC.main.style.LookupField",
    "NOC.main.pool.LookupField",
    "NOC.inv.interfaceprofile.LookupField",
    "NOC.sa.managedobject.LookupField",
  ],
  model: "NOC.inv.macdb.Model",
  search: true,
  searchPlaceholder: __("insert MAC address to search"),
  requirePlaceholder: __("type MAC address to search"),
  searchTooltip: __("Insert MAC address to this field one of format:<li>FULL: AA:AA:AA:AA:AA:AA</li><li>Left part: AA:AA:</li><li>Right part: :AA:AA</li>"),
  canCreate: false,
  rowClassField: "row_class",
  //
  columns: [
    {
      text: __("Mac Address"),
      dataIndex: "mac",
      width: 110,
    },
    {
      text: __("L2 Domain"),
      dataIndex: "l2_domain",
      renderer: NOC.render.Lookup("l2_domain"),
      flex: 1,
    },
    {
      text: __("Pool"),
      dataIndex: "pool",
      renderer: NOC.render.Lookup("pool"),
      flex: 1,
    },
    {
      text: __("Object Profile"),
      dataIndex: "object_profile",
      renderer: NOC.render.Lookup("object_profile"),
      flex: 1,
    },
    {
      text: __("Vlan"),
      dataIndex: "vlan",
      width: 40,
    },
    {
      flex: 1,
      text: __("Managed Object"),
      renderer: NOC.render.Lookup("managed_object"),
      dataIndex: "managed_object",
    },
    {
      flex: 1,
      text: __("Interface"),
      dataIndex: "interface",
    },
    {
      flex: 1,
      text: __("Description"),
      dataIndex: "description",
    },
    {
      text: __("Last Changed"),
      dataIndex: "last_changed",
      width: 150,
    },
  ],
  //
  filters: [
    {
      title: __("By Profile"),
      name: "interface_profile",
      ftype: "lookup",
      lookup: "inv.interfaceprofile",
    },
    {
      title: __("By Object"),
      name: "managed_object",
      ftype: "lookup",
      lookup: "sa.managedobject",
    },
  ],
  gridToolbar: [
    {
      xtype: "radiogroup",
      width: 250,
      items: [
        {
          checked: true,
          xtype: "radio",
          boxLabel: __("MAC DB"),
          name: "source",
          inputValue: "macdb",
        },
        {
          xtype: "radio",
          boxLabel: __("MAC History"),
          name: "source",
          inputValue: "history",
        },
      ],
      listeners: {
        change: function(field, newValue){
          var searchField = this.up("toolbar").down("[name=search_field]"),
            app = this.up("[appId=inv.macdb]"),
            query = searchField.getValue();
          if(newValue.source === "macdb"){
            searchField.clearInvalid();
            searchField.setEmptyText(app.searchPlaceholder);
          }
          if(newValue.source === "history"){
            searchField.markInvalid(__("Required field"));
            searchField.setEmptyText(app.requirePlaceholder);
          }
          if(!Ext.isEmpty(query)){
            app.onSearch(query);
          }
        },
      },
    },
  ],
  //
  initComponent: function(){
    this.callParent();
    var favFilter = this.down("[name=fav_status]");
    this.searchField.onChange = Ext.EmptyFunction;
    this.searchField.setTriggers({
      clear: {
        cls: "x-form-clear-trigger",
        hidden: true,
        handler: function(field){
          field.setValue("");
          field.up("[appId=inv.macdb]").onSearch("");
        },
      },
    });
    this.searchField.on("change", function(field, value){
      var trigger = field.getTrigger("clear");
      if(trigger){
        trigger.setVisible(!!value);
      }
    });
    favFilter.up().remove(favFilter);
  },
  //
  createForm: function(){
    this.form = Ext.create("NOC.inv.macdb.MACLogForm", {app: this});
    return this.form;
  },
  //
  onEditRecord: function(record){
    this.showItem(this.ITEM_FORM).preview(record);
  },
  //
  onSearch: function(query){
    Ext.apply(this.currentQuery, this.down("radiogroup").getValue());
    if(query && query.length > 0){
      this.currentQuery.__query = query;
    } else{
      delete this.currentQuery.__query;
    }
    this.reloadStore();
  },
});
