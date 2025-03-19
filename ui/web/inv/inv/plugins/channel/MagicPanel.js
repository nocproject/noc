//---------------------------------------------------------------------
// inv.inv Channel Magic Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.channel.MagicPanel");

Ext.define("NOC.inv.inv.plugins.channel.MagicPanel", {
  extend: "Ext.panel.Panel",
  alias: "widget.invchannelmagic",
  layout: "fit",
  defaultListenerScope: true,
  items: [
    {
      xtype: "grid",
      itemId: "invChannelMagicGrid",
      scrollable: "y",
      height: 310,
      stateful: true,
      stateId: "inv.inv-channel-magic-grid",
      allowDeselect: true,
      store: new Ext.data.Store({
        fields: ["controller", "controller__label", "start_endpoint", "start_endpoint__label", "end_endpoint", "end_endpoint__label"],
        data: [],
      }),
      columns: [
        {
          xtype: "actioncolumn",
          width: 25,
          stopSelection: false,
          items: [
            {
              glyph: NOC.glyph.plus,
              tooltip: __("Create or update channel"),
              handler: function(view, rowIndex){
                var grid = view.up("grid"),
                  selectionModel = grid.getSelectionModel();
                selectionModel.select(rowIndex);
                view.up("invchannelmagic").fireEvent("magicopenparamsform");
              },
            },
          ],
          defaultRenderer: function(v, meta, record, rowIdx, colIdx, store, view){
            var prefix = Ext.baseCSSPrefix,
              scope = this.origScope || this,
              item = this.items[0],
              ret, disabled, tooltip,
              glyph = Ext.isEmpty(record.get("channel_id")) ? NOC.glyph.plus : NOC.glyph.edit,
              glyphFontFamily = Ext._glyphFontFamily;

            item.tooltip = Ext.isEmpty(record.get("channel_id")) ? __("Create channel") : __("Update channel");
            ret = Ext.isFunction(this.origRenderer) ? this.origRenderer.apply(scope, arguments) || "" : "";

            meta.tdCls += " " + Ext.baseCSSPrefix + "action-col-cell";

            disabled = item.disabled || (item.isDisabled ? item.isDisabled.call(item.scope || scope, view, rowIdx, colIdx, item, record) : false);
            tooltip = disabled ? null : (item.tooltip || (item.getTip ? item.getTip.apply(item.scope || scope, arguments) : null));

            if(!item.hasActionConfiguration){
              item.stopSelection = this.stopSelection;
              item.disable = Ext.Function.bind(this.disableAction, this, [0], 0);
              item.enable = Ext.Function.bind(this.enableAction, this, [0], 0);
              item.hasActionConfiguration = true;
            }
            ret += "<span role='button' unselectable='on' class='" +
                    prefix + "action-col-icon " +
                    prefix + "icon-el " +
                    prefix + "action-col-0" +
                    " " + (disabled ? prefix + "item-disabled" : " ") + "' " +
                    "style='font-family:" + glyphFontFamily + ";font-size:16px;padding-right:2px;line-height:normal" +
                    (Ext.isFunction(item.getColor) ? ";color:" + item.getColor.apply(item.scope || scope, arguments) : (item.color ? ";color:" + item.color : "")) + "'" +
                    (tooltip ? " data-qtip='" + tooltip + "'" : "") +
                    ">&#" + glyph + ";</span>";
            return ret;
          },
        },
        {
          text: __("Channel"),
          dataIndex: "channel_name",
          width: 250,
          renderer: function(v){
            if(v){
              return v;
            }
            return "<i>" + __("Create new...") + "</i>";
          },
        },
        {
          text: __("Start"),
          dataIndex: "start_endpoint",
          flex: 1,
          renderer: NOC.render.Lookup("start_endpoint"),
        },
        {
          text: __("End"),
          dataIndex: "end_endpoint",
          flex: 1,
          renderer: NOC.render.Lookup("end_endpoint"),
        },
        {
          text: __("Controller"),
          dataIndex: "controller",
          renderer: NOC.render.Lookup("controller"),
          width: 150,
        },
        {
          text: __("Status"),
          dataIndex: "status",
          width: 50,
          renderer: function(v){
            return {
              "new": "<i class='fa fa-plus' style='color:" + NOC.colors.emerald + "' title='New'></i>",
              "done": "<i class='fa fa-check' style='color:" + NOC.colors.yes + "' title='Done'></i>",
              "broken": "<i class='fa fa-exclamation-triangle' style='color:" + NOC.colors.no + "' title='Broken'></i>",
            }[v];
          },
        },
      ],
      selModel: {
        selType: "rowmodel",
        listeners: {
          selectionchange: "onSelectionChange",
          deselect: "onDeselectChange",
        },
      },
      listeners: {
        rowDblClick: function(){
          this.up("invchannelmagic").fireEvent("magicopenparamsform");
        },
      },
    },
  ],
  onSelectionChange: function(selModel, selections){
    if(selections.length > 0){
      var isNew = Ext.isEmpty(selections[0].get("channel_id")),
        title = isNew ? __("Create new channel") : __("Update channel") + " " + selections[0].get("channel_name");
      this.fireEvent("magicselectionchange", false, isNew ? __("Create") : __("Update"), title);
    }
  },
  onDeselectChange: function(){
    this.fireEvent("magicselectionchange", true, __("Create"), __("Create new channel"));
  },
});