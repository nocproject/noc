###
    Комбо выбора колонки источника данных.
###
Ext.define 'Report.view.configurator.filters.ColumnCombo',
	extend: 'Ext.form.field.ComboBox'
	xtype: 'configuratorFiltersColumnCombo'
	
	allowBlank: false
	queryMode: 'local'
	displayField: 'title'
	valueField: 'type'
	
	store:
		model: 'Report.model.config.Column'