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
		@getCombo().setReadOnly(false)
		@getCombo().setEmptyText('')
	
	###
        Блокирует комбо выбора источника данных.
	###
	disableCombo: () ->
		@getCombo().setReadOnly(true)
		@getCombo().setEmptyText('Любой')
		
	privates:
		
		###
            @return {Ext.form.field.ComboBox} Виджет список источников.
		###
		getCombo: () ->
			@down('#combo')