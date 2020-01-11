//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.monitor.SelectionGrid');
Ext.define('NOC.sa.monitor.SelectionGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.sa.selectionGrid',

    bind: {
        store: '{objectsStore}'
    },
    reference: 'selectionGrid',
    border: 1,
    emptyText: __('Not Found'),
    stateful: true,
    stateId: 'monitor.selectionGrid',
    selModel: {
        mode: 'MULTI',
        selType: 'checkboxmodel'
    },
    columns: [
        {
            text: __('ID'),
            tooltip: __('ID'),
            hidden: true,
            dataIndex: 'id',
            width: 60
        },
        {
            dataIndex: 'name',
            text: __('Managed object'),
            tooltip: __('Managed object'),
            width: 120,
            renderer: 'onRenderTooltip'
        },
        {
            dataIndex: 'address',
            text: __('IP Address'),
            tooltip: __('SA Profile'),
            width: 60,
            renderer: 'onRenderTooltip'
        },
        {
            dataIndex: 'profile_name',
            text: __('SA Profile'),
            tooltip: __('SA Profile'),
            width: 60,
            renderer: 'onRenderTooltip'
        },
        {
            dataIndex: 'b_time_start',
            text: __('Time start'),
            tooltip: __('Time start'),
            width: 40,
            renderer: 'onRenderTooltip',
            sortable: false
        },
        {
            dataIndex: 'b_last_success',
            text: __('Box Last success'),
            tooltip: __('Box Last success'),
            width: 40,
            renderer: 'onRenderTooltip',
            sortable: false
        },
        {
            dataIndex: 'b_time',
            text: __('Box Completed Time'),
            tooltip: __('Box Completed Time'),
            width: 40,
            renderer: 'onRenderTooltip',
            sortable: false
        },
        {
            dataIndex: 'b_status',
            text: __('Box Status'),
            tooltip: __('Box Status'),
            width: 50,
            sortable: false,
            renderer: 'onRenderStatus'
        },
        {
            dataIndex: 'b_duration',
            text: __('Box Duration'),
            tooltip: __('Box Duration'),
            width: 50,
            sortable: false,
            renderer: 'onRenderStatus'
        },
        {
            dataIndex: 'b_last_status',
            text: __('Box Last status'),
            tooltip: __('Box Last status'),
            width: 50,
            sortable: false,
            renderer: 'onRenderStatus'
        },
        {
            dataIndex: 'p_time_start',
            text: __('Periodic Time start'),
            tooltip: __('Periodic Time start'),
            width: 40,
            renderer: 'onRenderTooltip',
            sortable: false
        },
        {
            dataIndex: 'p_last_success',
            text: __('Periodic Last success'),
            tooltip: __('Periodic Last success'),
            width: 40,
            renderer: 'onRenderTooltip',
            sortable: false
        },
        {
            dataIndex: 'p_time',
            text: __('Periodic Completed Time'),
            tooltip: __('Periodic Completed Time'),
            width: 40,
            renderer: 'onRenderTooltip',
            sortable: false
        },
        {
            dataIndex: 'p_status',
            text: __('Periodic Status'),
            tooltip: __('Periodic Status'),
            width: 50,
            sortable: false,
            renderer: 'onRenderStatus'
        },
        {
            dataIndex: 'p_duration',
            text: __('Periodic Duration'),
            tooltip: __('Periodic Duration'),
            width: 50,
            sortable: false,
            renderer: 'onRenderStatus'
        },
        {
            dataIndex: 'p_last_status',
            text: __('Periodic Last status'),
            tooltip: __('Periodic Last status'),
            width: 50,
            sortable: false,
            renderer: 'onRenderStatus'
        }
    ],
    tbar: [
        {
            glyph: NOC.glyph.refresh,
            tooltip: __('Reload data'),
            enableToggle: true,
            handler: 'onReload'
        },
        {
            text: __('Select All'),
            glyph: NOC.glyph.plus_circle,
            tooltip: __('Select all records from buffer (screen)'),
            handler: 'onSelectAll'
        },
        {
            text: __('Unselect All'),
            glyph: NOC.glyph.minus_circle,
            bind: {
                disabled: '{!selectionGrid.selection}'
            },
            tooltip: __('Unselect All'),
            handler: 'onUnselectAll'
        },
        {
            text: __('Filter'),
            glyph: NOC.glyph.filter,
            tooltip: __('Show/Hide Filter'),
            handler: 'onShowFilter'
        },
        {
            text: __("Export"),
            glyph: NOC.glyph.arrow_down,
            tooltip: __('Export all records from buffer (screen)'),
            handler: 'onExport'
        },
        '->',
        {
            xtype: 'box',
            bind: {
                html: __('Selected') + ': {total.selection}'
            }
        }
    ],
    listeners: {
        selectionchange: 'onSelectionChange',
        rowdblclick: 'onRowDblClick'
    }
});