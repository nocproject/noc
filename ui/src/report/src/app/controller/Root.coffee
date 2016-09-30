###
	Управление корневой частью приложения, виевпортом и генерацией контента по конфигу.
###
Ext.define 'Report.controller.Root',
	extend: 'Ext.app.Controller'
	id: 'root'
	
	requires: [
		'Report.model.Gate'
		'Report.model.API'
		'Report.model.StoreField'
	]
	
	models: [
		'config.Column'
		'config.Dashboard'
		'config.Filter'
		'config.Root'
		'config.Widget'
		'query.Query'
		'wellspring.List'
	]
	
	listen:
		component:
			'rootMain #userButton':
				click: 'openNocUserMenu'
			'rootMain #addDashboard':
				click: 'showDashboardLibrary'

	###
		@private
		@readonly
		@property {Report.model.config.Root} reportConfig Конфигурация всего отчета.
	###
	reportConfig: null
	
	###
		Создание отчета по сохраненному на сервере конфигу.
	###
	makeReport: () ->
		@getReportConfig (data) ->
			model = Ext.create 'Report.data.Root'
			
			model.set data
			
			switch model.get 'version'
				when null or '0.1'
					Ext.create('Report.factory.V_0_1').make model
					
	privates:

		###
			Получение конфига отчета с сервера.
			@param {Function} next
			Следующий шаг, принимающий первым параметром результат в виде объекта.
		###
		getReportConfig: (next) ->
			Report.model.Gate.send(
				Report.model.API.config,
				null,
				next.bind @
			)
	
		###
			Сохранение конфига отчета на сервере.
			@param {Object} data Конфиг.
			@param {Function} next
			Следующий шаг, принимающий первым параметром результат в виде объекта.
		###
		setReportConfig: (data, next) ->
			Report.model.Gate.post(
				Report.model.API.config,
				data,
				next.bind @
			)

		###
			Открывает меню пользователя.
		###
		openNocUserMenu: () ->
			console.log 'show noc user menu' # TODO
	
		###
			Показывает библиотеку дашбордов.
			@param {Report.view.root.AddDashboard} button Кнопка добавления дашборда.
		###
		showDashboardLibrary: (button) ->
			
			###
				Оповещает о необходимости добавления дашборда.
				@param {Report.controller.Root} this Контроллер.
				@param {Report.view.root.TabPanel} tabPanel Панель вкладок для добавления дашбордов.
				@param {Report.view.root.AddDashboard} button Кнопка добавления дашборда.
			###
			@fireEvent 'addDashboardAction', @, button