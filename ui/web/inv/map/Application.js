//---------------------------------------------------------------------
// inv.map application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.Application");

Ext.define("NOC.inv.map.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.inv.networksegment.TreeCombo",
    "NOC.inv.map.MapPanel",
    "NOC.inv.map.inspectors.SegmentInspector",
    "NOC.inv.map.inspectors.ManagedObjectInspector",
    "NOC.inv.map.inspectors.LinkInspector",
    "NOC.inv.map.inspectors.CloudInspector",
    "NOC.inv.map.inspectors.CPEInspector",
    "NOC.inv.map.Legend",
    "NOC.inv.map.MiniMap",
    "NOC.inv.map.Basket",
    "Ext.ux.form.SearchField",
  ],
  rightWidth: 250,
  zoomLevels: [
    [0.25, "25%"],
    [0.5, "50%"],
    [0.75, "75%"],
    [1.0, "100%"],
    [1.25, "125%"],
    [1.5, "150%"],
    [2.0, "200%"],
    [3.0, "300%"],
    [4.0, "400%"],
  ],
  initComponent: function(){
    var me = this;

    me.readOnly = !me.hasPermission("write");
    me.searchField = Ext.create({
      xtype: "searchfield",
      minWidth: 150,
      triggers: {
        clear: {
          cls: "x-form-clear-trigger",
          hidden: true,
          weight: -1,
          scope: me,
          handler: function(field){
            field.setValue(null);
            this.resetSearchButton();
          },
        },
      },
      listeners: {
        scope: me,
        specialkey: me.searchByText,
        change: function(field, value){
          if(value == null || value === ""){
            field.getTrigger("clear").hide();
            return;
          }
          field.getTrigger("clear").show();
          this.resetSearchButton();
        },
      },
    });

    me.searchButton = Ext.create({
      xtype: "button",
      text: __("Search"),
      scope: me,
      handler: me.onSearch,
    });

    me.segmentCombo = Ext.create("NOC.core.TreeCombo", {
      restUrl: "/inv/map",
      fieldLabel: __("Segment"),
      labelWidth: 50,
      labelAlign: "left",
      listAlign: "left",
      minWidth: 400,
      emptyText: __("Select segment..."),
      appId: "inv.map",
      rootNode: {
        label: __("All Maps"),
        id: "_root_",
        level: 0,
      },
      listeners: {
        scope: me,
        select: me.onSelectSegment,
      },
    });

    me.zoomCombo = Ext.create("Ext.form.ComboBox", {
      store: me.zoomLevels,
      width: 60,
      value: 1.0,
      valueField: "zoom",
      displayField: "label",
      listeners: {
        scope: me,
        select: me.onZoom,
      },
    });

    me.reloadButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.refresh,
      iconAlign: "right",
      textAlign: "right",
      html: "0 " + __("sec"),
      width: 95,
      tooltip: __("Reload and It has been since the last update"),
      scope: me,
      handler: me.onReload,
    });

    me.editButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.edit,
      enableToggle: true,
      disabled: true,
      tooltip: __("Edit map"),
      scope: me,
      handler: me.onEdit,
    });

    me.rotateButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.rotate_right,
      tooltip: __("Rotate"),
      disabled: true,
      scope: me,
      handler: me.onRotate,
    });

    me.saveButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.save,
      tooltip: __("Save"),
      disabled: true,
      scope: me,
      handler: me.onSave,
    });

    me.revertButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.undo,
      tooltip: __("Revert"),
      disabled: true,
      scope: me,
      handler: me.onRevert,
    });

    me.newLayoutButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.medkit,
      tooltip: __("New layout"),
      disabled: me.readOnly,
      scope: me,
      handler: me.onNewLayout,
    });

    me.addressIPButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.tag,
      tooltip: __("Name/IP device"),
      enableToggle: true,
      // disabled: me.readOnly,
      scope: me,
      handler: me.onChangeName,
    });

    me.segmentInspector = Ext.create("NOC.inv.map.inspectors.SegmentInspector", {
      app: me,
      readOnly: me.readOnly,
    });

    me.managedObjectInspector = Ext.create("NOC.inv.map.inspectors.ManagedObjectInspector", {
      app: me,
      readOnly: me.readOnly,
    });

    me.objectGroupInspector = Ext.create("NOC.inv.map.inspectors.ObjectGroupInspector", {
      app: me,
      readOnly: me.readOnly,
    });

    me.objectSegmentInspector = Ext.create("NOC.inv.map.inspectors.ObjectSegmentInspector", {
      app: me,
      readOnly: me.readOnly,
    });

    me.objectPortalInspector = Ext.create("NOC.inv.map.inspectors.ObjectPortalInspector", {
      app: me,
      readOnly: me.readOnly,
    });

    me.linkInspector = Ext.create("NOC.inv.map.inspectors.LinkInspector", {
      app: me,
      readOnly: me.readOnly,
    });

    me.cloudInspector = Ext.create("NOC.inv.map.inspectors.CloudInspector", {
      app: me,
      readOnly: me.readOnly,
    });

    me.cpeInspector = Ext.create("NOC.inv.map.inspectors.CPEInspector", {
      app: me,
      readOnly: me.readOnly,
    });

    me.legendPanel = Ext.create("NOC.inv.map.Legend", {
      collapsed: true,
      region: "south",
      width: this.rightWidth,
      collapsible: true,
      collapseMode: undefined,
      header: false,
      hideCollapseTool: true,
    });

    me.miniMapPanel = Ext.create("NOC.inv.map.MiniMap", {
      region: "south",
      width: this.rightWidth,
      collapsible: true,
      collapseMode: undefined,
      header: false,
      hideCollapseTool: true,
    });

    me.basketPanel = Ext.create("NOC.inv.map.Basket", {
      collapsed: true,
      region: "south",
      width: this.rightWidth,
      collapsible: true,
      collapseMode: undefined,
      header: false,
      hideCollapseTool: true,
      listeners: {
        scope: me,
        createmaintaince: function(data){
          me.mapPanel.newMaintaince(data.items);
        },
        addtomaintaince: function(data){
          me.mapPanel.addToMaintaince(data.items)
        },
      },
    });

    me.inspectorPanel = Ext.create("Ext.panel.Panel", {
      app: me,
      layout: "card",
      region: "center",
      scrollable: true,
      items: [
        me.segmentInspector,
        me.managedObjectInspector,
        me.linkInspector,
        me.objectGroupInspector,
        me.objectSegmentInspector,
        me.objectPortalInspector,
        me.cpeInspector,
      ],
    });

    me.rightPanel = Ext.create("Ext.panel.Panel", {
      layout: "border",
      dock: "right",
      width: this.rightWidth,
      items: [
        me.inspectorPanel,
        me.basketPanel,
        me.miniMapPanel,
        me.legendPanel,
      ],
    });

    me.mapPanel = Ext.create("NOC.inv.map.MapPanel", {
      app: me,
      readOnly: me.readOnly,
      listeners: {
        scope: me,
        mapready: me.onMapReady,
        changed: me.onChanged,
        openbasket: function(){
          if(me.basketPanel.collapsed){
            me.basketButton.setPressed();
          }
        },
        renderdone: function(){
          me.miniMapPanel.scaleContentToFit();
          if(me.selectedObjectId){
            me.selectCell(me.mapPanel.objectNodes[me.selectedObjectId]);
          }
        },
        updateTick: function(text){
          var btnInnerEl = me.reloadButton.btnInnerEl,
            btnEl = me.reloadButton.btnEl;
          if(me.reloadButton.rendered){
            btnInnerEl.setHtml(text || "&#160;");
            btnEl[text ? "addCls" : "removeCls"](me._textCls);
            btnEl[text ? "removeCls" : "addCls"](me._noTextCls);
          }
        },
        onSelectCell: me.selected,
        onUnselectCell: me.selected,
      },
    });

    me.viewMapButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.globe,
      tooltip: __("Show static map"),
      enableToggle: true,
      toggleGroup: "overlay",
      pressed: true,
      scope: me,
      handler: me.onSetOverlay,
      mapOverlay: me.mapPanel.LO_NONE,
    });

    me.viewLoadButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.line_chart,
      tooltip: __("Show interface load"),
      enableToggle: true,
      toggleGroup: "overlay",
      scope: me,
      handler: me.onSetOverlay,
      mapOverlay: me.mapPanel.LO_LOAD,
    });

    me.viewStpButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.sitemap,
      enableToggle: true,
      disabled: true,
      tooltip: __("Show STP topology"),
      scope: me,
      handler: me.onStp,
    });

    me.viewAllNodeButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.eye,
      enableToggle: true,
      pressed: false,
      tooltip: __("Show all nodes"),
      scope: me,
      handler: me.onReload,
    });

    me.legendButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.info,
      tooltip: __("Show/Hide legend"),
      enableToggle: true,
      listeners: {
        scope: me,
        toggle: me.onLegend,
      },
    });

    me.miniMapButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.map,
      tooltip: __("Show/Hide miniMap"),
      enableToggle: true,
      pressed: true,
      listeners: {
        scope: me,
        toggle: me.onMiniMap,
      },
    });

    me.basketButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.shopping_basket,
      tooltip: __("Show/Hide basket"),
      enableToggle: true,
      listeners: {
        scope: me,
        toggle: me.onBasket,
      },
    });

    Ext.apply(me, {
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            me.segmentCombo,
            "-",
            me.zoomCombo,
            me.reloadButton,
            "-",
            me.searchField,
            me.searchButton,
            "-",
            me.editButton,
            me.saveButton,
            me.revertButton,
            me.newLayoutButton,
            me.rotateButton,
            "-",
            me.addressIPButton,
            me.viewMapButton,
            me.viewLoadButton,
            "-",
            me.viewStpButton,
            me.viewAllNodeButton,
            "->",
            me.basketButton,
            me.miniMapButton,
            me.legendButton,
          ],
        },
        me.rightPanel,
      ],
      items: [me.mapPanel],
    });
    me.callParent();
  },

  loadSegment: function(segmentId){
    var me = this;

    if(me.segmentCombo.getValue() == null){
      me.segmentCombo.restoreById(segmentId, true);
    }
    me.setHistoryHash(segmentId);
    me.mapPanel.loadSegment(me.generator, segmentId);
    me.currentSegmentId = segmentId;
    // @todo: Restrict to permissions
    me.editButton.setDisabled(me.readOnly);
    me.saveButton.setDisabled(true);
    me.setStateMapButtons(!me.editButton.pressed);
    me.editButton.setPressed(false);
    // me.inspectSegment();
    me.viewMapButton.setPressed(true);
    me.viewStpButton.setPressed(false);
    me.zoomCombo.setValue(1.0);
    me.mapPanel.setZoom(1.0);
    me.mapPanel.paper.clearGrid();
  },

  onMapReady: function(){
    var me = this, hash, segmentId;

    if(me.getCmd() === "history"){
      me.generator = me.noc.cmd.args[0];
      segmentId = me.noc.cmd.args[1];
      if(typeof segmentId === "string"){
        if(segmentId.indexOf(":") !== -1){
          hash = segmentId.split(":");
          segmentId = hash[0];
          me.selectedObjectId = hash[1];
        }
      }
      me.loadSegment(segmentId);
      if(me.noc.cmd.args.length > 2){
        me.selectedObjectId = me.noc.cmd.args[2];
      }
    }
    me.miniMapPanel.createMini(me.mapPanel);
  },

  onSelectSegment: function(combo, record, opts){
    var me = this;
    if(record){
      me.generator = record.get("generator");
      me.loadSegment(record.get("id"));
    }
  },

  onZoom: function(combo, record, opts){
    var me = this;
    me.mapPanel.setZoom(record.get("field1"));
  },

  inspectSegment: function(){
    var me = this;
    me.inspectorPanel.getLayout().setActiveItem(
      me.segmentInspector,
    );
    if(me.currentSegmentId){
      me.segmentInspector.preview(me.currentSegmentId, null);
    }
  },

  inspectManagedObject: function(objectId){
    var me = this;
    me.inspectorPanel.getLayout().setActiveItem(
      me.managedObjectInspector,
    );
    me.managedObjectInspector.preview(me.currentSegmentId, objectId);
  },

  inspectLink: function(linkId){
    var me = this;
    me.inspectorPanel.getLayout().setActiveItem(
      me.linkInspector,
    );
    me.linkInspector.preview(me.currentSegmentId, linkId);
  },

  inspectCloud: function(linkId){
    var me = this;
    me.inspectorPanel.getLayout().setActiveItem(
      me.cloudInspector,
    );
    me.cloudInspector.preview(me.currentSegmentId, linkId);
  },

  inspectObjectGroup: function(objectId){
    var me = this;
    me.inspectorPanel.getLayout().setActiveItem(
      me.objectGroupInspector,
    );
    me.objectGroupInspector.preview(me.currentSegmentId, objectId);
  },

  inspectObjectSegment: function(objectId){
    var me = this;
    me.inspectorPanel.getLayout().setActiveItem(
      me.objectSegmentInspector,
    );
    me.objectSegmentInspector.preview(me.currentSegmentId, objectId);
  },

  inspectObjectPortal: function(objectId){
    var me = this;
    me.inspectorPanel.getLayout().setActiveItem(
      me.objectPortalInspector,
    );
    me.objectPortalInspector.preview(me.currentSegmentId, objectId);
  },

  inspectCPE: function(objectId){
    var me = this;
    me.inspectorPanel.getLayout().setActiveItem(
      me.cpeInspector,
    );
    me.cpeInspector.preview(me.currentSegmentId, objectId);
  },

  onEdit: function(){
    var me = this;
    me.mapPanel.paper.clearGrid();
    if(me.editButton.pressed){
      me.mapPanel.setOverlayMode(0);
      me.mapPanel.paper.setGrid({
        name: "doubleMesh",
        args: [
          {color: "#bdc3c7", thickness: 1}, // settings for the primary mesh
          {color: "#bdc3c7", scaleFactor: 5, thickness: 2}, //settings for the secondary mesh
        ],
      });
      me.mapPanel.paper.drawGrid();
      me.viewMapButton.setPressed(true);
      me.saveButton.setDisabled(true);
      me.setStateMapButtons(false);
    } else{
      me.setStateMapButtons(true);
      me.saveButton.setDisabled(true);
    }
    me.mapPanel.setInteractive(me.editButton.pressed);
  },

  onSave: function(){
    var me = this;
    me.mapPanel.save();
  },

  onRevert: function(){
    var me = this;
    me.loadSegment(me.currentSegmentId);
    me.editButton.setPressed(true);
  },

  onReload: function(){
    var me = this;
    me.loadSegment(me.currentSegmentId);
  },

  onChanged: function(){
    var me = this;
    if(me.editButton.pressed){
      me.saveButton.setDisabled(me.readOnly);
      me.setStateMapButtons(me.readOnly);
    }
  },

  onCloseApp: function(){
    var me = this;
    me.mapPanel.stopPolling();
  },

  onSetOverlay: function(button){
    var me = this;
    me.mapPanel.setOverlayMode(button.mapOverlay);
  },

  onNewLayout: function(btn, ev){
    var me = this,
      forceSpring = ev.shiftKey;
    Ext.Msg.show({
      title: __("Reset Layout"),
      message: __("Would you like to reset current layout and generate new?"),
      icon: Ext.Msg.QUESTION,
      buttons: Ext.Msg.YESNO,
      fn: function(btn){
        if(btn === "yes"){
          me.mapPanel.resetLayout(forceSpring);
        }
      },
    });
  },

  onRotate: function(){
    var me = this;
    me.mapPanel.onRotate();
  },

  onChangeName: function(){
    var me = this;
    me.mapPanel.changeLabelText(me.addressIPButton.pressed);
  },

  onStp: function(){
    var me = this;
    me.mapPanel.setStp(me.viewStpButton.pressed);
  },

  onLegend: function(){
    this.legendPanel.toggleCollapse();
  },

  onMiniMap: function(){
    this.miniMapPanel.toggleCollapse();
  },

  onBasket: function(){
    this.basketPanel.toggleCollapse();
  },

  setStateMapButtons: function(state){
    var me = this;
    me.newLayoutButton.setDisabled(state);
    me.rotateButton.setDisabled(state);
    me.revertButton.setDisabled(state);
    if(!me.mapPanel.normalize_position){
      me.rotateButton.setDisabled(true);
    }
  },

  searchByText: function(field, e){
    if(Ext.EventObject.ENTER === e.getKey()){
      this.onSearch();
    }
  },

  onSearch: function(){
    var searched = undefined,
      value = this.searchField.getValue();
    if(!Ext.isEmpty(value)){
      Ext.Object.eachValue(this.mapPanel.objectNodes, function(node){
        var name = node.attributes.name.replace(/\n/g, "");
        if(name.indexOf(value) !== -1){
          searched = node;
          return false;
        }
      });
      this.selectCell(searched);
    }
  },

  selectCell: function(searched){
    var scrollX, scrollY,
      zoom = this.zoomCombo.getValue(),
      getScroll = function(pos, offset){
        var value = pos * zoom - offset;
        return value > 0 ? value : 0;
      };
    this.selectedObjectId = null;
    if(searched && searched.isElement()){
      var offsetX = this.mapPanel.getWidth() / 2,
        offsetY = this.mapPanel.getHeight() / 2;
      this.searchButton.setText(__("Search"));
      scrollX = getScroll(searched.attributes.position.x, offsetX);
      scrollY = getScroll(searched.attributes.position.y, offsetY);
      this.mapPanel.onCellSelected(this.mapPanel.paper.findViewByModel(searched));
      this.selectedObjectId = searched.attributes.data.id;
    } else{
      scrollX = scrollY = 0;
      this.mapPanel.unhighlight();
      this.searchButton.setText(__("Not found"));
    }
    this.setHistoryHash(this.currentSegmentId);
    this.mapPanel.setPaperDimension();
    this.mapPanel.scrollTo(scrollX, scrollY);
  },

  resetSearchButton: function(){
    this.searchButton.setText(__("Search"));
    this.mapPanel.setPaperDimension();
  },

  selected: function(objectId){
    var me = this;
    me.selectedObjectId = objectId;
    me.setHistoryHash(me.currentSegmentId);
  },

  getHistoryHash: function(){
    var me = this;
    if(me.currentSegmentId){
      me.mapPanel.loadSegment(me.generator, me.currentSegmentId);
    }
    return me.currentHistoryHash;
  },

  setHistoryHash: function(segmentId){
    var me = this;
    me.currentHistoryHash = [me.appId, me.generator || "segment"].concat([].slice.call([segmentId], 0)).join("/");
    if(me.selectedObjectId){
      me.currentHistoryHash += ":" + me.selectedObjectId;
    }
    Ext.History.setHash(me.currentHistoryHash);
  },
});
