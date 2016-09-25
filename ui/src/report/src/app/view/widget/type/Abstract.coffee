###
    Абстрактный виджет.
###
Ext.define 'Report.view.widget.type.Abstract',
	extend: 'Ext.container.Container'
	
	layout: 'fit'
	
	config:
	
		###
			@cfg {Ext.data.Store} store Стор данных виджета.
		###
		store: null
	
		###
			@cfg {Ext.data.Store} columns Колонки источника данных в виде стора с моделями.
		###
		columns: null