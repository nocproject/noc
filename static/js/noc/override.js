//---------------------------------------------------------------------
// ExtJS overrides
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Patching ExtJS " + Ext.getVersion().version);
//---------------------------------------------------------------------
// Patches for ExtJS 5.0.0 errors
// Review after any ExtJS upgrade
//---------------------------------------------------------------------

//---------------------------------------------------------------------
// ExtJS core function improvements
//---------------------------------------------------------------------

//
// Override grid column state ids
//
Ext.override(Ext.grid.column.Column, {
    getStateId: function() {
        return this.stateId || this.dataIndex || this.headerId;
    }
});
//
// Override form field labels
//
Ext.override(Ext.form.Panel, {
    initComponent: function() {
        var me = this,
            applyLabelStyle = function(field) {
                if((field.xtype == "fieldset") || (field.xtype == "container")) {
                    Ext.each(field.items.items, function(f) {
                        applyLabelStyle(f);
                    });
                } else {
                    if(!field.allowBlank) {
                        field.labelClsExtra = "noc-label-required";
                    }
                }
            };
        me.on("beforeadd", function(form, field) {
            applyLabelStyle(field);
        });
        me.callParent();
    }
});

Ext.override(Ext.tree.Column, {
    cellTpl: [
        '<tpl for="lines">',
        '<img src="{parent.blankUrl}" class="{parent.childCls} {parent.elbowCls}-img ',
        '{parent.elbowCls}-<tpl if=".">line<tpl else>empty</tpl>" role="presentation"/>',
        '</tpl>',


        '<img src="{blankUrl}" class="{childCls} {elbowCls}-img {elbowCls}',
        '<tpl if="isLast">-end</tpl><tpl if="expandable">-plus {expanderCls}</tpl>" role="presentation"/>',
        '<tpl if="checked !== null">',
        '<input type="button" {ariaCellCheckboxAttr}',
        ' class="{childCls} {checkboxCls}<tpl if="checked"> {checkboxCls}-checked</tpl>"/>',
        '</tpl>',


        '<tpl if="glyphCls">' ,
            '<i class="{glyphCls}" style="font-size: 16px"></i> ',
        '<tpl else>',
            '<img src="{blankUrl}" role="presentation" class="{childCls} {baseIconCls} ',
            '{baseIconCls}-<tpl if="leaf">leaf<tpl else>parent</tpl> {iconCls}"',
            '<tpl if="icon">style="background-image:url({icon})"</tpl>/>',
        '</tpl>',
        '<tpl if="href">',
        '<a href="{href}" role="link" target="{hrefTarget}" class="{textCls} {childCls}">{value}</a>',
        '<tpl else>',
        '<span class="{textCls} {childCls}">{value}</span>',
        '</tpl>'
    ],
    initTemplateRendererData: function (value, metaData, record, rowIdx, colIdx, store, view) {
        var me = this,
            renderer = me.origRenderer,
            data = record.data,
            parent = record.parentNode,
            rootVisible = view.rootVisible,
            lines = [],
            parentData,
            iconCls = data.iconCls,
            glyphCls;

        while (parent && (rootVisible || parent.data.depth > 0)) {
            parentData = parent.data;
            lines[rootVisible ? parentData.depth : parentData.depth - 1] =
            parentData.isLast ? 0 : 1;
            parent = parent.parentNode;
        }

        if(iconCls && iconCls.indexOf("fa fa-") == 0) {
            glyphCls = iconCls;
            iconCls = null;
        }

        return {
            record: record,
            baseIconCls: me.iconCls,
            glyphCls: glyphCls,
            iconCls: iconCls,
            icon: data.icon,
            checkboxCls: me.checkboxCls,
            checked: data.checked,
            elbowCls: me.elbowCls,
            expanderCls: me.expanderCls,
            textCls: me.textCls,
            leaf: data.leaf,
            expandable: record.isExpandable(),
            isLast: data.isLast,
            blankUrl: Ext.BLANK_IMAGE_URL,
            href: data.href,
            hrefTarget: data.hrefTarget,
            lines: lines,
            metaData: metaData,
            // subclasses or overrides can implement a getChildCls() method, which can
            // return an extra class to add to all of the cell's child elements (icon,
            // expander, elbow, checkbox).  This is used by the rtl override to add the
            // "x-rtl" class to these elements.
            childCls: me.getChildCls ? me.getChildCls() + ' ' : '',
            value: renderer ? renderer.apply(me.origScope, arguments) : value
        };
    },
    treeRenderer: function(value, metaData, record, rowIdx, colIdx, store, view){
        var me = this,
            cls = record.get('cls'),
            rendererData;

        if (cls) {
            metaData.tdCls += ' ' + cls;
        }
        rendererData = me.initTemplateRendererData(value, metaData, record, rowIdx, colIdx, store, view);

        return me.getTpl('cellTpl').apply(rendererData);
    }
});
