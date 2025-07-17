//---------------------------------------------------------------------
// inv.inv BoM Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.bom.BoMPanel");

Ext.define("NOC.inv.inv.plugins.bom.BoMPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.bom.BoMModel",
    "NOC.inv.inv.plugins.bom.BoMController",
  ],
  itemId: "invinvbom",
  title: __("BoM"),
  closable: false,
  controller: "bom",
  layout: "fit",
  viewModel: {
    data: {
      searchText: "",
      totalCount: 0,
      currentId: undefined,
    },
  },
  tbar: [
    {
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      handler: "onReload",
    },
    {
      xtype: "textfield",
      itemId: "searchText",
      emptyText: __("Search..."),
      width: 400,
      bind: {
        value: "{searchText}",
      },
      listeners: {
        change: function(field, newValue){
          var trigger = field.getTrigger("clear");
          if(newValue){
            trigger.show();
          } else{
            trigger.hide();
          }
        },
      },
      triggers: {
        clear: {
          cls: "x-form-clear-trigger",
          hidden: true,
          handler: function(field){
            field.setValue("");
            var grid = field.up("panel").down("gridpanel"),
              store = grid.getStore();
            store.clearFilter();
            field.getTrigger("clear").hide();
          },
        },
      },
    },
    {
      glyph: NOC.glyph.download,
      tooltip: __("Export to CSV"),
      handler: "onExport",
    },
    "->",
    {
      xtype: "tbtext",
      style: {
        paddingRight: "20px",
      },
      bind: {
        html: __("Total") + ": {totalCount}",
      },
    },
  ],
  items: [
    {
      xtype: "gridpanel",
      border: false,
      stateful: true,
      stateId: "inv.inv-bom-grid",
      allowDeselect: true,
      store: {   
        model: "NOC.inv.inv.plugins.bom.BoMModel",
        // sorters: [
        //   {property: "model", direction: "ASC"},
        // ],
      },
      features: [{
        ftype: "grouping",
      }],
      scrollable: "y",
      columns: [
        {
          xtype: "glyphactioncolumn",
          width: 25,
          items: [
            {
              tooltip: __("View"),
              handler: function(view, rowIndex, colIndex, item, e, record){
                var app = view.up("[appId=inv.inv]"),
                  plugin = view.up("#invinvbom");
                if(app && plugin.getViewModel().get("currentId") !== record.id){
                  app.showObject(record.id);
                }
              },
            },
          ],
          defaultRenderer: function(v, meta, record, rowIdx, colIdx, store, view){
            var me = this,
              prefix = Ext.baseCSSPrefix,
              scope = me.origScope || me,
              item = me.items[0],
              ret, disabled, tooltip,
              currentId = view.up("#invinvbom").getViewModel().get("currentId"),
              glyph = record.id !== currentId ? NOC.glyph.eye : "",
              glyphFontFamily = Ext._glyphFontFamily;

            ret = Ext.isFunction(me.origRenderer) ? me.origRenderer.apply(scope, arguments) || "" : "";

            meta.tdCls += " " + Ext.baseCSSPrefix + "action-col-cell";

            disabled = item.disabled || (item.isDisabled ? item.isDisabled.call(item.scope || scope, view, rowIdx, colIdx, item, record) : false);
            tooltip = disabled ? null : (item.tooltip || (item.getTip ? item.getTip.apply(item.scope || scope, arguments) : null));

            if(!item.hasActionConfiguration){
              item.stopSelection = me.stopSelection;
              item.disable = Ext.Function.bind(me.disableAction, me, [0], 0);
              item.enable = Ext.Function.bind(me.enableAction, me, [0], 0);
              item.hasActionConfiguration = true;
            }
            if(glyph){
              ret += '<span role="button" unselectable="on" class="' +
                prefix + "action-col-icon " +
                prefix + "icon-el " +
                prefix + "action-col-0" +
                " " + (disabled ? prefix + "item-disabled" : " ") + '" ' +
                'style="font-family:' + glyphFontFamily + ";font-size:16px;padding-right:2px;line-height:normal" +
                (Ext.isFunction(item.getColor) ? ";color:" + item.getColor.apply(item.scope || scope, arguments) : (item.color ? ";color:" + item.color : "")) + '"' +
                (tooltip ? ' data-qtip="' + tooltip + '"' : "") +
                ">&#" + glyph + ";</span>";
            }
            return ret;
          },
        },
        {
          text: __("Vendor"),
          dataIndex: "vendor",
          width: 150,
        },
        {
          text: __("Model"),
          dataIndex: "model",
          width: 250,
        },
        {
          text: __("Location"),
          dataIndex: "location",
          flex: 1,
          renderer: function(v){
            return v.join(" > ")
          },
        },
        {
          text: __("Serial"),
          dataIndex: "serial",
          width: 150,
        },
        {
          text: __("Asset#"),
          dataIndex: "asset_no",
          width: 150,
        },
        {
          text: __("Revision"),
          dataIndex: "revision",
          width: 100,
        },
        {
          text: __("Version"),
          dataIndex: "fw_version",
          width: 100,
        },
      ],
    },
  ],
  initComponent: function(){
    this.callParent();

    var store = this.down("grid").getStore(),
      filters = store.getFilters();

    store.on("datachanged", this.getController().onDataChanged, this);
    store.setGroupField("vendor");
    this.getViewModel().bind({
      bindTo: {
        searchText: "{searchText}",
      },
      single: false,
    }, function(data){
      var bomFilter = filters.find("_id", "invBoMFilter");
      if(bomFilter){
        filters.remove(bomFilter);
      }
      filters.add({
        id: "invBoMFilter",
        filterFn: function(record){
          var text = data.searchText.toLowerCase(),
            vendor = record.get("vendor").toLowerCase(),
            model = record.get("model").toLowerCase(),
            serial = record.get("serial").toLowerCase(),
            asset_no = record.get("asset_no").toLowerCase(),
            revision = record.get("revision").toLowerCase(),
            fw_version = record.get("fw_version").toLowerCase();
          return vendor.includes(text) ||
              model.includes(text) ||
              serial.includes(text) ||
              asset_no.includes(text) ||
              revision.includes(text) ||
              fw_version.includes(text)
        },
      });
    });
  },
  preview: function(data, objectId){
    var me = this,
      vm = me.getViewModel();
    if(Object.prototype.hasOwnProperty.call(data, "status") && !data.status){
      NOC.error(data.message);
      return
    }
    vm.set("currentId", objectId);
    this.down("grid").getStore().loadData(data.data);
  },
});
