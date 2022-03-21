

mapViewPage = {
    options: {
        mapViewContainerId: '',
        mapboxToken: ''
    },

    mapObject: null,
    
    createIcon: function createIcon(count, CSSclass) {
        return L.divIcon({
            className: `leaflet-marker-icon marker-cluster marker-cluster-single leaflet-zoom-animated leaflet-interactive ${ CSSclass }`,
            html: `<div><span>${count}</span></div>`,
            iconSize: [40, 40],
            popupAnchor: [-10,-10],
        })
    },
    
    cssClassedIconCreateFunction: function cssClassedIconCreateFunction(cssClass) {
        return (function (cluster) {
            var childCount = cluster.getChildCount();
            var cssClasses = ['marker-cluster']
            var c = ' marker-cluster-'
            if (childCount < 10) {
                c += 'small'
            } else if (childCount < 100) {
                c += 'medium'
            } else {
                c += 'large'
            }
            cssClasses.push(c)
            cssClasses.push(cssClass)
            return new L.DivIcon({
                 html: '<div><span>' + childCount + '</span></div>',
                 className: cssClasses.join(' '), 
                 iconSize: new L.Point(40, 40) 
            })
        })
    },


    initializeMap: function initializeMap() {
        let mapOptions = {
            center: [51.13, 10.018],
            zoom: 6
        }
    
        let tileLayerURL = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}@2x?access_token=' + this.options.mapboxToken
        let tileLayerOptions = {
            attribution: ' <a href="https://www.mapbox.com/about/maps/">© Mapbox</a> | <a href="http://www.openstreetmap.org/copyright">© OpenStreetMap</a> | <a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a> | Icons by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">flaticon.com</a>',
            maxZoom: 18,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            preferCanvas: true,
          }
    
        this.mapObject = L.map(this.options.mapViewContainerId,mapOptions)
        L.tileLayer(tileLayerURL, tileLayerOptions).addTo(this.mapObject);    

        // Enhance MarkerCluster - override getChildCount
        L.MarkerCluster.prototype.getChildCount = function (){
            const children = this.getAllChildMarkers()
            return children.reduce((sum,marker) => (sum + marker.options.itemCount),0)
        }

    },

    onResizeWindow: function onResizeWindow() {
        let height = $(window).height()
        let navHeight = $('.navbar').outerHeight()
        let searchHeight = $('.search-map').innerHeight()
        let footerHeight = $('.footer').innerHeight()
        let isSearchBarActive = document.getElementById('organisation_navbar') !== null
        let newHeight = height - navHeight - ( isSearchBarActive ? searchHeight : 0 ) - footerHeight
        $(document.getElementById(mapViewPage.options.mapViewContainerId)).height(newHeight)
        mapViewPage.mapObject.invalidateSize()
    },

    registerEventHandlers : function registerEventHandlers(document, window) {
        $(window).on("resize", (event) => { this.onResizeWindow() }).trigger("resize")
    },

    loadMapMarkers : async function loadMapMarkers() {
    },

    createMapMarkers : function addMapMarkers(markers, createMarkerFunction) {
        let markerArray = []
        
        for (countryCode in markers) {
            for (zipCodeKey in markers[countryCode]) {
                let zipCode = markers[countryCode][zipCodeKey]
                markerArray.push(createMarkerFunction(zipCode.latitude, zipCode.longitude, countryCode, zipCode.city, zipCode.plz, zipCode.count))
            }
        }

        return markerArray
    }
}
$.extend(mapViewPage.options, pageOptions)

document.addEventListener("DOMContentLoaded", function domReady() {

    mapViewPage.initializeMap()
    mapViewPage.loadMapMarkers()
    mapViewPage.registerEventHandlers(document, window)

})
