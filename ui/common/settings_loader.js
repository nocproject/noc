// The function needed in modules that are not a part of the NOC.
// Such as alarmheat, monmap

class SettingsLoader {
    run = function() {
        var httpRequest = new XMLHttpRequest();
        httpRequest.open("GET", "/main/desktop/settings/", false);
        httpRequest.send();
        console.log("!!!");
        console.log("!!! Receiving NOC settings");
        console.log("!!!");
        if(httpRequest.status === 200) {
            var setup = JSON.parse(httpRequest.responseText);
            console.log("!!! NOC settings successfully received")
            if(typeof NOC === "undefined") {
                window.NOC = {
                    settings: {}
                };
            }
            NOC.settings = {
                systemId: setup.system_uuid ? setup.system_uuid : null,
                brand: setup.brand,
                installation_name: setup.installation_name,
                preview_theme: setup.preview_theme,
                language: setup.language,
                logo_url: setup.logo_url,
                logo_width: setup.logo_width,
                logo_height: setup.logo_height,
                branding_color: setup.branding_color,
                branding_background_color: setup.branding_background_color,
                enable_search: setup.enable_search,
                gitlab_url: setup.gitlab_url,
                collections: {
                    allow_sharing: setup.collections.allow_sharing,
                    allow_overwrite: setup.collections.allow_overwrite,
                    project_id: setup.collections.project_id
                },
                gis: {
                    base: {
                        enable_blank: setup.gis.base.enable_blank,
                        "enable_osm": setup.gis.base.enable_osm,
                        "enable_google_roadmap": setup.gis.base.enable_google_roadmap,
                        "enable_google_hybrid": setup.gis.base.enable_google_hybrid,
                        "enable_google_sat": setup.gis.base.enable_google_sat,
                        "enable_google_terrain": setup.gis.base.enable_google_terrain,
                        "enable_tile1": setup.gis.base.enable_tile1,
                        "enable_tile2": setup.gis.base.enable_tile2,
                        "enable_tile3": setup.gis.base.enable_tile3,
                        "enable_yandex_roadmap": setup.gis.base.enable_yandex_roadmap,
                        "enable_yandex_hybrid": setup.gis.base.enable_yandex_hybrid,
                        "enable_yandex_sat": setup.gis.base.enable_yandex_sat,
                    },
                    custom: {
                        tile1: {
                            name: setup.gis.custom.tile1.name,
                            url: setup.gis.custom.tile1.url,
                            subdomains: setup.gis.custom.tile1.subdomains,
                        },
                        tile2: {
                            name: setup.gis.custom.tile2.name,
                            url: setup.gis.custom.tile2.url,
                            subdomains: setup.gis.custom.tile2.subdomains,
                        },
                        tile3: {
                            name: setup.gis.custom.tile3.name,
                            url: setup.gis.custom.tile3.url,
                            subdomains: setup.gis.custom.tile3.subdomains,
                        }
                    },
                    "yandex_supported": setup.gis.yandex_supported,
                    default_layer: setup.gis.default_layer,
                },
                traceExtJSEvents: setup.traceExtJSEvents,
                helpUrl: setup.helpUrl,
                helpBranch: setup.helpBranch,
                helpLanguage: setup.helpLanguage,
                timezone: setup.timezone,
                enable_remote_system_last_extract_info: setup.enable_remote_system_last_extract_info,
                enableHelp: setup.helpUrl && setup.helpUrl !== "",
                has_geocoder: setup.has_geocoder
            };
            return NOC.settings;
        } else {
            console.warn("!!! NOC settings receiving failed!")
            return {}
        }
    }
}

settingsLoader = new SettingsLoader()
