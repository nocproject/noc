//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Grid");

Ext.define("NOC.fm.alarm.view.grids.Grid", {
  extend: "Ext.grid.Panel",
  controller: "fm.alarm.GridController",
  requires: [
    "NOC.fm.alarm.view.grids.GridController",
    "NOC.fm.alarm.view.grids.GridViewTable",
    "Ext.ux.grid.column.GlyphAction",
  ],
  stateful: true,
  columns: [
    {
      text: __("ID"),
      dataIndex: "id",
      width: 150,
      hidden: true,
    },
    {
      xtype: "glyphactioncolumn",
      width: 22 * 4,
      sortable: false,
      items: [
        {
          glyph: NOC.glyph.star,
          tooltip: __("Mark/Unmark"),
          getColor: function(cls, meta, r){
            return r.get("fav_status") ? NOC.colors.starred : NOC.colors.unstarred;
          },
          handler: "onFavItem",
        },
        {
          glyph: NOC.glyph.globe,
          tooltip: __("Show map"),
          handler: "onShowMap",
        },
        {
          glyph: NOC.glyph.map_o,
          tooltip: __("Show neighbor map"),
          handler: "onShowNeighborMap",
        },
        {
          glyph: NOC.glyph.eye,
          tooltip: __("Show object"),
          handler: "onShowObject",
        },
      ],
    },
    {
      text: __("Status"),
      dataIndex: "status",
      width: 60,
      renderer: function(v, _, record){
        var STATUS_MAP = {
            A: "Active",
            C: "Archived",
          },
          value = NOC.render.Choices(STATUS_MAP)(v);
        if(record.get("isInMaintenance")) value = '<span title="' + __("Under maintaintance") + '">' +
                    '<i class="fa fa-wrench" aria-hidden="true"></i>&nbsp;' + value + "</span>";
        return value;
      },
      hidden: true,
    },
    {
      text: __("Time/Duration"),
      dataIndex: "timestamp",
      width: 120,
      renderer: function(v, _, record){
        return NOC.render.DateTime(record.get("timestamp")) +
                    "<br/>" +
                    NOC.render.Duration(record.get("duration"));
      },
    },
    {
      text: __("Start"),
      dataIndex: "timestamp",
      width: 120,
      hidden: true,
      renderer: NOC.render.DateTime,
    },
    {
      text: __("Stop"),
      dataIndex: "clear_timestamp",
      width: 120,
      hidden: true,
      renderer: function(v){
        if(v === null){
          return "-"
        } else{
          return NOC.render.DateTime(v)
        }
      },
    },
    {
      text: __("Duration"),
      dataIndex: "duration",
      width: 120,
      hidden: true,
      renderer: NOC.render.Duration,
    },
    {
      text: __("Object/Segment"),
      dataIndex: "managed_object",
      width: 250,
      renderer: function(v, _, record){
        return record.get("managed_object__label") + "<br/>" + record.get("segment__label");
      },
    },
    {
      text: __("Location"),
      dataIndex: "location",
      width: 250,
      renderer: function(v, _, record){
        return record.get("location_1") + "<br/>" + record.get("location_2");
      },
    },
    {
      text: __("Address/Platform"),
      dataIndex: "address",
      width: 120,
      renderer: function(v, _, record){
        return record.get("address") +
                    "<br/>" +
                    (record.get("platform") || "");
      },
    },
    {
      text: __("Severity"),
      dataIndex: "severity",
      width: 70,
      renderer: function(v, _, record){
        return record.get("severity__label") +
                    "<br/>" +
                    record.get("severity");
      },
    },
    {
      xtype: "actioncolumn",
      text: __("Ack"),
      flex: 1,
      innerCls: undefined,
      defaultRenderer: function(v, cellValues, record, rowIdx, colIdx, store, view){
        var scope = this.origScope || this,
          items = this.items,
          len = items.length,
          i, item, ret, disabled, tooltip, altText, icon,
          tooltipFromData = this.getView().tooltip(record);

        ret = Ext.isFunction(this.origRenderer) ? this.origRenderer.apply(scope, arguments) || "" : "";

        cellValues.tdCls += " " + Ext.baseCSSPrefix + "action-col-cell";
        for(i = 0; i < len; i++){
          item = items[i];
          icon = item.icon;
          if(item.renderer){
            ret += "<div>" + item.renderer(undefined, undefined, record) + "</div>";
            continue;
          }
          disabled = item.disabled || (item.isDisabled ? item.isDisabled.call(item.scope || scope, view, rowIdx, colIdx, item, record) : false);
          tooltip = disabled ? null : (tooltipFromData || (item.getTip ? item.getTip.apply(item.scope || scope, arguments) : null));
          altText = item.getAltText ? item.getAltText.apply(item.scope || scope, arguments) : item.altText || this.altText;

          if(!item.hasActionConfiguration){
            item.stopSelection = this.stopSelection;
            item.disable = Ext.Function.bind(this.disableAction, this, [i], 0);
            item.enable = Ext.Function.bind(this.enableAction, this, [i], 0);
            item.hasActionConfiguration = true;
          }

          ret += "<" + (icon ? "img" : "div") + ' tabIndex="0" role="button"' + (icon ? (' alt="' + altText + '" src="' + item.icon + '"') : "") +
                        ' class="' + this.actionIconCls + " " + Ext.baseCSSPrefix + "action-col-" + String(i) + " " +
                        (disabled ? this.disabledCls + " " : " ") +
                        (Ext.isFunction(item.getClass) ? item.getClass.apply(item.scope || scope, arguments) : (item.iconCls || this.iconCls || "")) + '"' +
                        (tooltip ? ' data-qclass="noc-alarm-tooltip" data-qtip="' + tooltip + '"' : "") + (icon ? "/>" : "></div>");
        }
        return ret;
      },
      items: [
        {
          handler: function(view, rowIndex, colIndex, item, e, record){
            var isUnAck = Ext.isEmpty(record.get("ack_user")),
              appController = this.up("[itemId=fm-alarm]").getController(),
              successFn = function(status){
                if(status){
                  view.up("[itemId=fm-alarm]").getController().reloadActiveGrid();
                }
              };
            appController.acknowledgeDialog(record.id, !isUnAck, successFn);
          },
          getClass: function(v, _, record){
            return "x-fa fa-" + (record.get("ack_user") ? "toggle-on" : "toggle-off");
          },
          isDisabled: function(view, rowIndex, colIndex, item, record){
            var isActive = record.get("status") === "A" || false;
            return !(view.up("[itemId=fm-alarm]").permissions["acknowledge"] && isActive);
          },
        },
        {
          renderer: function(v, _, record){
            return record.get("ack_user")
              ? record.get("ack_user")
                            + "-"
                            + Ext.Date.format(record.get("ack_ts"), "Y-m-d H:i")
              : "-";
          },
        },
      ],
    },
    {
      text: __("Comments Qty"),
      width: 40,
      renderer: function(v, _, record){
        var commentsLength = record.get("logs").length;
        return '<div data-qclass="noc-alarm-tooltip" data-qtip="' + this.getView().tooltip(record)
                    + '"><div class="x-fa fa-' + (commentsLength ? "commenting" : "comment-o")
                    + '"></div><span style="padding-left: 5px;">'
                    + commentsLength + "</span></div>";
      },
    },
    {
      text: __("Subject/Class"),
      dataIndex: "subject",
      flex: 1,
      sortable: false,
      renderer: function(v, _, record){
        return record.get("subject") +
                    "<br/>" +
                    record.get("alarm_class__label");
      },
    },
    {
      text: __("Summary/TT"),
      dataIndex: "summary",
      width: 150,
      sortable: false,
      renderer: function(v, _, record){
        var filter, r = [], summary = record.get("summary"),
          tt = record.get("escalation_tt") || false,
          ee = record.get("escalation_error") || false;
        if(this.getViewModel()){
          filter = this.getViewModel().get("displayFilter.hasProfiles");
        }
        if(!Ext.Object.isEmpty(filter)
                    && filter.array && filter.array.length > 0
                    && (record.get("total_services") || record.get("total_subscribers"))){
          var data = Ext.Array.map(record.get("total_subscribers").concat(record.get("total_services")), function(item){
            return {
              id: item.profile,
              label: item.profile__label,
              icon: item.glyph,
              summary: item.summary,
              display_order: item.display_order,
            }
          });
          summary = this.up("[reference=fm-alarm-list]").getController().generateSummaryHtml(data, filter);
        }
        r.push(summary);
        if(tt){
          r.push('<a href="/api/card/view/tt/' + tt + '/" target="_blank">' + tt + "</a>");
        } else{
          if(ee){
            r.push('<i class="fa fa-exclamation-triangle"></i> Error')
          }
        }
        return r.join("<br>");
      },
    },
    {
      text: __("Objects"),
      dataIndex: "total_objects",
      width: 30,
      align: "right",
      sortable: false,
    },
    {
      text: __("Events"),
      dataIndex: "events",
      width: 30,
      align: "right",
      sortable: false,
    },
    {
      text: __("Grouped"),
      dataIndex: "total_grouped",
      width: 30,
      align: "right",
      sortable: false,
    },
  ],
  viewConfig: {
    xclass: "NOC.fm.alarm.view.grids.GridViewTable",
  },
});
