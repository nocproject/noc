//---------------------------------------------------------------------
// fm.alarm.tagfield widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Tagfield");

Ext.define("NOC.fm.alarm.view.grids.Tagfield", {
    extend: "Ext.form.field.Tag",
    alias: "widget.fm.alarm.tagfield",
    controller: "fm.alarm.tagfield",
    requires: [
        "NOC.fm.alarm.view.grids.TreePicker",
        "NOC.fm.alarm.view.grids.TagfieldController"
    ],
    displayField: "label",
    valueField: "id",
    queryMode: "remote",
    queryParam: "__query",
    queryCaching: false,
    queryDelay: 200,
    minChars: 2,
    pageSize: true,
    isTree: false,
    pickerPosition: "left", // right | left
    store: {
        fields: ["id", "label"],
        pageSize: 25,
        proxy: {
            type: "rest",
            pageParam: "__page",
            startParam: "__start",
            limitParam: "__limit",
            sortParam: "__sort",
            extraParams: {
                "__format": "ext"
            },
            reader: {
                type: "json",
                rootProperty: "data",
                totalProperty: "total",
                successProperty: "success"
            }
        }
    },
    config: {
        selected: null
    },
    twoWayBindable: [
        "selected"
    ],
    listeners: {
        change: "onChangeTagValue"
    },
    initComponent: function() {
        this.store.proxy.url = this.url;
        if(this.isTree) {
            // this.treePicker = this.createTreePicker();
            this.triggers.picker.cls = "theme-classic fas fa fa-folder-open-o";
            this.treePicker = Ext.create({
                xtype: "fm.alarm.treepicker",
                displayField: this.displayField,
                scope: this,
            });
        }
        // Fix combobox when use remote paging
        this.pickerId = this.getId() + '-picker';
        this.callParent();
    },
    setSelected: function(value, skip) {
        this.callParent([value]);
        if(!skip) {
            this.setWidgetValues(value);
        }
    },
    setWidgetValues: function(data) {
        this.setSelection(data);
    },
    onTriggerClick: function(el) {
        if(!el) {
            return;
        }
        if(this.isTree) {
            var position,
                heightAbove = this.getPosition()[1] - Ext.getBody().getScroll().top,
                heightBelow = Ext.Element.getViewportHeight() - heightAbove - this.getHeight();
            this.treePicker.setWidth(this.getWidth());
            this.treePicker.height = Math.max(heightAbove, heightBelow) - 5;
            this.setEditable(false);
            position = this.getPosition();
            if(this.pickerPosition === "left") {
                position[0] = position[0] - this.getWidth();
            } else if(this.pickerPosition === "right") {
                position[0] = position[0] + this.getWidth();
            }
            if(heightAbove > heightBelow) {
                position[1] -= this.treePicker.height - this.getHeight();
            }
            this.treePicker.showAt(position);
        } else {
            Ext.form.field.Tag.prototype.onTriggerClick.apply(this, arguments);
        }
    },
});
