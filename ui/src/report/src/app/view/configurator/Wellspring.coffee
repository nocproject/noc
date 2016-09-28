###
	Источник данных виджета и соответствующие колонки.
###
Ext.define 'Report.view.configurator.Wellspring',
	extend: 'Ext.container.Container'
	xtype: 'configuratorWellspring'
	
	items: [
		{
			itemId: 'point'
			xtype: 'combobox'
			fieldLabel: 'Источник данных'
			queryMode: 'local'
			displayField: 'name'
			valueField: 'id'
			store:
				model: 'Report.model.wellspring.List'
		}
		{
			itemId: 'grid'
			xtype: 'grid'
			store:
				model: 'Report.model.config.Column'
			columns: [
				{
					dataindex: 'title'
					text: 'Имя'
					flex: 1
				}
				{
					dataIndex: 'selected'
					xtype: 'checkcolumn'
				}
			]
		}
	]