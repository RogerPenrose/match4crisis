

mapViewPage = {
    options: {
        mapViewContainerId: '',
        accomodationOfferURL : '',
        transportationOfferURL : '',
        translationOfferURL : '',
        supporterListURL  : '',
        mapboxToken: '',
        isStudent: true,
        isHospital: true,
        createPopupTextTransportation  :  (countrycode,city, plz, count, url) => '',
        createPopupTextTranslation :  (countrycode,city, plz, count, url) => '',
        createPopupTextAccomodation :  (countrycode,city, plz, count, url) => '',
        createAccomodationCountText: (count) => '',
        createTransportationCountText: (count) => '',
        createTranslationCountText: (count) => '',
        createDigitalCountText: (count) => '',
        facilityIcon: new L.Icon.Default(),

    },

    mapObject: null,
    
    createAccomodationIcon: function createAccomodationIcon(count) {
        return L.divIcon({
            className: 'leaflet-marker-icon marker-cluster marker-cluster-single leaflet-zoom-animated leaflet-interactive accomodationMarker',
            html: `<div><span>${count}</span></div>`,
            iconSize: [40, 40],
            popupAnchor: [-10,-10],
        })
    },

    createTransportationIcon: function createTransportationIcon(count) {
        return L.divIcon({
            className: 'leaflet-marker-icon marker-cluster marker-cluster-single leaflet-zoom-animated leaflet-interactive transportationMarker',
            html: `<div><span>${count}</span></div>`,
            iconSize: [40, 40],
        })
    },

    createTranslationIcon: function createTranslationIcon(count) {
        return L.divIcon({
            className: 'leaflet-marker-icon marker-cluster marker-cluster-single leaflet-zoom-animated leaflet-interactive translationMarker',
            html: `<div><span>${count}</span></div>`,
            iconSize: [40, 40],
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
            attribution: ' <a href="https://www.mapbox.com/about/maps/">© Mapbox</a> | <a href="http://www.openstreetmap.org/copyright">© OpenStreetMap</a> | <a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>',
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
        let [ accomodations, transportations, translations ] = await Promise.all([$.get(this.options.accomodationOfferURL),$.get(this.options.transportationOfferURL),$.get(this.options.translationOfferURL)])
        // ACCOMODATIONS:
        var accomodationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('accomodationMarker'),
        });
        let accomodationMarkers = L.featureGroup.subGroup(accomodationClusterMarkerGroup, this.createMapMarkers(accomodations,(lat,lon,countrycode,city,plz,count) => {
            return L.marker([lon,lat],{ 
                icon:  this.createAccomodationIcon(count),
                itemCount: count,
           }).bindPopup(this.options.createPopupTextAccomodation(countrycode,city, plz, count, this.options.accomodationOfferURL.replace("COUNTRYCODE",countrycode).replace("PLZ",plz)))
        }))
        // TRANSPORTATIONS:

        var transportationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('transportationMarker'),
        });
        var transportationMarkers = L.featureGroup.subGroup(transportationClusterMarkerGroup, this.createMapMarkers(transportations,(lat,lon,countrycode,city,plz,count) => {
            return L.marker([lon,lat],{
                 icon:  this.createTransportationIcon(count),
                 itemCount: count,
            }).bindPopup(this.options.createPopupTextTransportation(countrycode,city, plz, count, this.options.transportationOfferURL.replace("COUNTRYCODE",countrycode).replace("PLZ",plz)))
        }))

        // TRANSLATIONS:
       
        var translationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('translationMarker'),
        });
        var translationMarkers = L.featureGroup.subGroup(translationClusterMarkerGroup, this.createMapMarkers(translations,(lat,lon,countrycode,city,plz,count) => {
            return L.marker([lon,lat],{
                 icon:  this.createTranslationIcon(count),
                 itemCount: count,
            }).bindPopup(this.options.createPopupTextTranslation(countrycode,city, plz, count, this.options.translationOfferURL.replace("COUNTRYCODE",countrycode).replace("PLZ",plz)))
        }))
        
        translationClusterMarkerGroup.addTo(this.mapObject)
        translationMarkers.addTo(this.mapObject)
        transportationClusterMarkerGroup.addTo(this.mapObject)
        transportationMarkers.addTo(this.mapObject)
        accomodationClusterMarkerGroup.addTo(this.mapObject)
        accomodationMarkers.addTo(this.mapObject)
        
        const countItems = (o) => {
            var count = 0
            for (countryCode in o) {
                for (zipCode in o[countryCode]) {
                    count += o[countryCode][zipCode].count
                }
            }
            return count
        }

        var overlays = {}
        overlays[this.options.createAccomodationCountText(countItems(accomodations))] = accomodationMarkers
        overlays[this.options.createTransportationCountText(countItems(transportations))] = transportationMarkers
        overlays[this.options.createTranslationCountText(countItems(translations))] = transportationMarkers

        L.control.layers(null, overlays, { collapsed: false, position: 'topright' }).addTo(this.mapObject)

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