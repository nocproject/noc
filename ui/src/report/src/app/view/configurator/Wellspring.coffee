###
	Источник данных виджета и соответствующие колонки.
###
Ext.define 'Report.view.configurator.Wellspring',
	extend: 'Ext.container.Container'
	xtype: 'configuratorWellspring'
	
	items: [
		{
			itemId: 'combo'
			xtype: 'combobox'
			fieldLabel: 'Источник данных'
			queryMode: 'local'
			displayField: 'name'
			valueField: 'id'
			emptyText: 'Любой'
			readOnly: true
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
					text: 'Колонка'
					flex: 1
				}
				{
					dataIndex: 'selected'
					xtype: 'checkcolumn'
					width: 25
				}
			]
		}
	]
	
	###
        Разблокирует комбо выбора источника данных.
	###
	enableCombo: () ->
		@down('#combo').setReadOnly(false)
	
	###
        Блокирует комбо выбора источника данных.
	###
	disableCombo: () ->
		@down('#combo').setReadOnly(true)