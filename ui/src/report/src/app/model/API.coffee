###
	Объект, содержащий список всех точек доступа к серверному апи.
###
Ext.define 'Report.model.API',
	singleton: true

	###
		@property {String} config Точка доступа до хранилища конфига.
	###
	config: ''
	
	###
		@property {String} query Точка доступа к произвольным запросам виджетов.
	###
	query: ''
	
	###
		@property {String} widgetsLibrary Точка доступа к библиотеке виджетов.
	###
	widgetsLibrary: ''