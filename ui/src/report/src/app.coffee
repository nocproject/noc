Ext.application(
	extend: 'Ext.app.Application'
	name: 'Report'
	
	requires: [
		'Report.view.root.Main'
		'Report.view.factory.V_0_1'
		'Report.model.MainDataTree'
	]
	
	controllers: [
		'Root'
		'Configurator'
		'Dashboard'
		'Library'
		'Widget'
	]
	
	mainView: 'Report.view.root.Main'
	
	constructor: () ->
		
		###
            @method getAllCmp
            Возвращает компоненты, соответствующие селектору.
            Аналог Ext.ComponentQuery.query
            @param {String} query Селектор.
        ###
		Report.getAllCmp = (query) -> Ext.ComponentQuery.query(query)
		
		###
            @method getCmp
            Возвращает первый найденый компонент, соответствующий селектору.
            Аналог Ext.ComponentQuery.query
            @param {String} query Селектор.
        ###
		Report.getCmp = (query) -> Ext.ComponentQuery.query(query)[0]
			
		@callParent arguments
	
	launch: () ->
		@showLoader()
		@makeReport()
		
	privates:
		
		###
            Отображает прелоадер.
		###
		showLoader: () ->
			body = Ext.getBody()
			windowWidthCenter = body.getWidth() / 2
			windowHeightCenter = body.getHeight() / 2
			loaderWidthCenter = 760 / 2
			loaderHeightCenter = 176 / 2
			decorativeTopMargin = 10
			startHideDelay = 1000
			hideDuration = 1200
			destroyDelay = 300
			
			loader = Ext.create 'Ext.Img',
				floating: true
				src: 'resources/img/SOVA.png'
				alt: 'SOVA logo'
				autoShow: true
				shadow: false
				x: windowWidthCenter - loaderWidthCenter
				y: windowHeightCenter - loaderHeightCenter + decorativeTopMargin
			
			loader.animate {
				delay: startHideDelay
				duration: hideDuration
				to:
					opacity: 0
			}
			
			setTimeout(
				() -> loader.destroy()
				startHideDelay + hideDuration + destroyDelay
			)

		###
            Создает-инициализирует отчет.
		###
		makeReport: () ->
			@controllers.getAt(0).makeReport()
)