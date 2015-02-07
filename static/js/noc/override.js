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

//
// Mark required fields and apply style templates
//
Ext.override(Ext.form.field.Base, {
    initComponent: function() {
        var me = this;
        // Apply label style
        if(!me.allowBlank) {
            me.labelClsExtra = "noc-label-required";
        }
        // Apply uiStyle
        if(me.uiStyle) {
            var style = Ext.apply({}, NOC.uiStyles[me.uiStyle] || {});
            if(me.labelWidth && style.width && (me.labelAlign === "left" || me.labelAlign == "right")) {
                style.width += me.labelWidth;
            }
            if(style.width && me.getTriggers) {
                var triggers = me.getTriggers();
                Ext.Array.each(Object.keys(triggers), function(v) {
                    style.width += 25;
                });
            }
            Ext.apply(me, style);
        }
        me.callParent();
    }
});

//
// Glyphs in tree column
//
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
// Trace events
if(NOC.settings.traceExtJSEvents) {
    console.log("Enabling event tracing");
    Ext.mixin.Observable.prototype.fireEvent =
        Ext.Function.createInterceptor(Ext.mixin.Observable.prototype.fireEvent, function () {
            console.log("EVENT", this.$className, arguments[0], Array.prototype.slice.call(arguments, 1));
            console.log("Stack trace:\n" + printStackTrace().join("\n"));
            return true;
        });
}

Ext.define('EXTJS-15862.tab.Bar', {
    override: 'Ext.tab.Bar',

    initComponent: function() {
        var me = this,
            initialLayout = me.initialConfig.layout,
            initialAlign = initialLayout && initialLayout.align,
            initialOverflowHandler = initialLayout && initialLayout.overflowHandler,
            layout;


        if (me.plain) {
            me.addCls(me.baseCls + '-plain');
        }


        me.callParent();


        me.setLayout({
            align: initialAlign || (me.getTabStretchMax() ? 'stretchmax' :
                    me._layoutAlign[me.dock]),
            overflowHandler: initialOverflowHandler || 'scroller'
        });


        // We have to use mousedown here as opposed to click event, because
        // Firefox will not fire click in certain cases if mousedown/mouseup
        // happens within btnInnerEl.
        me.on({
            mousedown: me.onClick,
            element: 'el',
            scope: me
        });
    }
});
