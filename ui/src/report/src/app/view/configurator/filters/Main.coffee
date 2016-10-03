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
			xtype: 'container'
			layout: 'hbox'
			items: [
				{
					xtype: 'tbspacer'
					flex: 1
				}
				{
					itemId: 'addFilter'
					xtype: 'button'
					iconCls: 'x-fa fa-plus'
					text: 'Добавить фильтр'
					margin: '6 2 16 0'
					handler: (button) ->
						button.up('configuratorFilters').down('grid').getStore().add({})
				}
			]
		}
		{
			itemId: 'grid'
			xtype: 'grid'
			plugins:
				ptype: 'cellediting'
				clicksToEdit: 1
			store:
				model: 'Report.model.config.Filter'
			columns: [
				{
					dataIndex: 'column'
					text: 'Колонка'
					flex: 1
					editor: [
						{
							xtype: 'configuratorFiltersColumnCombo'
						}
					]
				}
				{
					dataIndex: 'type'
					text: 'Тип фильтра'
					flex: 1
					editor: [
						{
							xtype: 'configuratorFiltersTypeCombo'
						}
					]
				}
				{
					xtype: 'actioncolumn'
					width: 25
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