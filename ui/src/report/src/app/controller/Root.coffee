###
	Управление корневой частью приложения, виевпортом и генерацией контента по конфигу.
###
Ext.define 'Report.controller.Root',
	extend: 'Ext.app.Controller'
	id: 'root'
	
	requires: [
		'Report.view.dashboard.Library'
		'Report.view.dashboard.Configurator'
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
		controller:
			'#dashboard':
				refresh: 'reportRefresh'
			'#widget':
				refresh: 'reportRefresh'
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
		Создание отчета по серверному конфигу.
	###
	makeReport: () ->
		@getReportConfig @makeReportByConfigObject.bind @
					
	privates:
		
		###
            Полное обновление вью отчета.
        ###
		reportRefresh: () ->
			@cleanReportView()
			@makeReportByMainDataTree()
	
		###
            Полностью очищает вью отчета.
        ###
		cleanReportView: () ->
			model = Report.model.MainDataTree
			
			switch model.get 'version'
				when ''
					Report.view.factory.V_0_1.clean()
				when '0.1'
					Report.view.factory.V_0_1.clean()
			
		###
            Создает отчет по объекту конфигурации.
            @param {Object} configObject Объект конфигурации.
        ###
		makeReportByConfigObject: (configObject) ->
			model = Report.model.MainDataTree
			
			model.set configObject
		
			@makeReportByMainDataTree()
		
		###
            Создает отчет по главному дереву данных, хранящему конфигурацию отчета.
        ###
		makeReportByMainDataTree: () ->
			model = Report.model.MainDataTree

			switch model.get 'version'
				when ''
					Ext.create('Report.view.factory.V_0_1').make model
				when '0.1'
					Ext.create('Report.view.factory.V_0_1').make model
			
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