###
	Абстрактная фабрика отчетов
###
Ext.define 'Report.view.factory.Abstract',
	
	config: {}
	
	constructor: (config) ->
		@initConfig config
		
		@callParent arguments

	###
		@method
		Создает отчет по входящей модели.
		@param {Ext.data.Model} model Модель отчета.
	###
	make: Ext.emptyFn