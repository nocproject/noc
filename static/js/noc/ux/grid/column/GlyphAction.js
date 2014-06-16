//---------------------------------------------------
// Ext.ux.grid.column.GlyphAction
//     ActionColumn utilizing glyphs as icons as well
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.grid.column.GlyphAction", {
    extend: "Ext.grid.column.Action",
    alias: "widget.glyphactioncolumn",

    defaultRenderer: function(v, meta, record, rowIdx, colIdx, store, view){
        var me = this,
            prefix = Ext.baseCSSPrefix,
            scope = me.origScope || me,
            items = me.items,
            len = items.length,
            i = 0,
            item, ret, disabled, tooltip,
            glyphFontFamily = Ext._glyphFontFamily;

        // Allow a configured renderer to create initial value (And set the other values in the "metadata" argument!)
        // Assign a new variable here, since if we modify "v" it will also modify the arguments collection, meaning
        // we will pass an incorrect value to getClass/getTip
        ret = Ext.isFunction(me.origRenderer) ? me.origRenderer.apply(scope, arguments) || '' : '';

        meta.tdCls += ' ' + Ext.baseCSSPrefix + 'action-col-cell';
        for (; i < len; i++) {
            item = items[i];

            disabled = item.disabled || (item.isDisabled ? item.isDisabled.call(item.scope || scope, view, rowIdx, colIdx, item, record) : false);
            tooltip = disabled ? null : (item.tooltip || (item.getTip ? item.getTip.apply(item.scope || scope, arguments) : null));

            // Only process the item action setup once.
            if (!item.hasActionConfiguration) {

                // Apply our documented default to all items
                item.stopSelection = me.stopSelection;
                item.disable = Ext.Function.bind(me.disableAction, me, [i], 0);
                item.enable = Ext.Function.bind(me.enableAction, me, [i], 0);
                item.hasActionConfiguration = true;
            }

            if(item.glyph) {
                // Use glyph
                ret += '<span role="button" unselectable="on" class="' +
                    prefix + 'action-col-icon ' +
                    prefix + 'icon-el ' +
                    prefix + 'action-col-' + String(i) +
                    ' ' + (disabled ? prefix + 'item-disabled' : ' ') + '" ' +
                    'style="font-family:' + glyphFontFamily + ';font-size:16px;padding-right:2px;line-height:normal' +
                    (item.color ? ';color:' + item.color : '') + '"' +
                    (tooltip ? ' data-qtip="' + tooltip + '"' : '') +
                    '>&#' + item.glyph + ';</span>';
            } else {
                // Use icon
                ret += '<img role="button" alt="' + (item.altText || me.altText) + '" src="' + (item.icon || Ext.BLANK_IMAGE_URL) +
                    '" class="' + prefix + 'action-col-icon ' + prefix + 'action-col-' + String(i) + ' ' + (disabled ? prefix + 'item-disabled' : ' ') +
                    ' ' + (Ext.isFunction(item.getClass) ? item.getClass.apply(item.scope || scope, arguments) : (item.iconCls || me.iconCls || '')) + '"' +
                    (tooltip ? ' data-qtip="' + tooltip + '"' : '') + ' />';
            }
        }
        return ret;
    }
});
