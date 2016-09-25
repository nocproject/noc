###
    Список фильтров.
###
Ext.define 'Report.view.configurator.filters.Main',
	extend: 'Ext.container.Container'
	xtype: 'configuratorFilters'
	
	requires: [
		'Report.view.configurator.filters.ColumnCombo'
		'Report.view.configurator.filters.TypeCombo'
	]
	
	items: [
		{
			itemId: 'grid'
			xtype: 'grid'
			title: 'Список фильтров'
			tbar: [
				'->'
				{
					itemId: 'addFilter'
					xtype: 'button'
					text: 'Добавить'
				}
			]
			plugins:
				ptype: 'cellediting'
				clicksToEdit: 1
			store:
				model: 'Report.model.config.Filter'
			columns: [
				{
					dataIndex: 'type'
					editor: [
						{
							xtype: 'configuratorFiltersTypeCombo'
						}
					]
				}
				{
					dataIndex: 'column'
					editor: [
						{
							xtype: 'configuratorFiltersColumnCombo'
						}
					]
				}
				{
					xtype: 'actioncolumn'
					items: [
						{
							iconCls: 'x-fa fa-close'
							handler: (grid, index) -> grid.getStore().removeAt(index)
						}
					]
				}
			]
		}
	]