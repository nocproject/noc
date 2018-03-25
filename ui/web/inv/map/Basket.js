//---------------------------------------------------------------------
// Basket
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.inv.map.Basket');

Ext.define('NOC.inv.map.Basket', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.basket',
    controller: 'basket',

    requires: [
        'NOC.inv.map.BasketController',
        'NOC.inv.map.BasketViewModel'
    ],

    // viewModel: 'default',
    viewModel: {
        type: 'basket'
    },
    height: 300,
    scrollable: true,
    hideHeaders: true,
    reference: 'basketGrid',
    emptyText: __('basket empty'),
    tbar: [
        {
            xtype: 'button',
            text: __("All"),
            glyph: NOC.glyph.minus_circle,
            handler: 'onDeleteAllClick',
            bind: {
                disabled: '{!hasRecords}'
            }
        },
        {
            xtype: 'button',
            tooltip: __("Delete object(s)"),
            glyph: NOC.glyph.minus_circle,
            handler: 'onDeleteClick',
            bind: {
                disabled: '{!basketGrid.selection}'
            }
        },
        {
            xtype: 'button',
            tooltip: __("Add to exist maintaince"),
            glyph: NOC.glyph.plus,
            handler: 'onAddToMaintainceClick',
            bind: {
                disabled: '{!hasRecords}'
            }
        },
        {
            xtype: 'button',
            tooltip: __("Create new maintaince"),
            glyph: NOC.glyph.file,
            handler: 'onCreateMaintainceClick',
            bind: {
                disabled: '{!hasRecords}'
            }
        },
        {
            xtype: 'button',
            tooltip: __("Export"),
            glyph: NOC.glyph.arrow_down,
            handler: 'onExportClick',
            bind: {
                disabled: '{!hasRecords}'
            }
        }
    ],
    selModel: {
        mode: 'SIMPLE',
        selType: 'checkboxmodel'
    },
    store: {
        storeId: 'basketStore',
        fields: ['object', 'object__label', 'address', 'platform', 'time'],
        data: []
    },
    columns: [{
        text: 'Object',
        dataIndex: 'object__label',
        flex: 1
    }]
});