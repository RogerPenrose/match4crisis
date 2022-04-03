function initMap(){
    const input = document.getElementById("location");

    const autocomplete = initMapsAutocomplete()

    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
            // User entered the name of a Place that was not suggested and
            // pressed the Enter key, or the Place Details request failed.
            return;
        }

        // If the place has a geometry, then present it on a map.
        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
            setGetParameter([
                ["location", input.value], 
                ["lat", place.geometry.location.lat()], 
                ["lng", place.geometry.location.lng()], 
                ["bb", JSON.stringify(place.geometry.viewport)]
            ])
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(15);
            setGetParameter([
                ["location", input.value], 
                ["lat", place.geometry.location.lat()], 
                ["lng", place.geometry.location.lng()]
            ])
        }        
    });

    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    loc = urlParams.get('location')
    if (loc) {
        input.setAttribute("value", loc)
    }

    lat = urlParams.get('lat')
    lng = urlParams.get('lng')

    viewport_set = false;
    let map;
    if (lat !== null && lng !== null){
        lat = parseFloat(lat);
        lng = parseFloat(lng);

        if (!isNaN(lat) && !isNaN(lng)){
            map = new google.maps.Map(document.getElementById("map"), {
                center: { lat: parseFloat(lat), lng: parseFloat(lng)},
                zoom: 16,
                mapTypeControl: false,
                fullscreenControl: false,
            });

            viewport_set = true
        }
    }
    if (!viewport_set) {
        map = new google.maps.Map(document.getElementById("map"), {
            center: { lat: 50.8, lng:10 },
            zoom: 6,
            mapTypeControl: false,
            fullscreenControl: false
        });
    }

    if (urlParams.get("bb")){
        try{
            map.fitBounds(JSON.parse(urlParams.get("bb")));
        } catch {}
    }

    map.setOptions({
        styles: [
            {
              featureType: "poi",
              elementType: "labels.text",
              stylers: [
                {
                  visibility: "off"
                }
              ]
            },
            {
              featureType: "poi.business",
              stylers: [
                {
                  visibility: "off"
                }
              ]
            }
          ]
    });

    map.addListener("bounds_chang", () => {
        setGetParameter([
            ["bb", JSON.stringify(map.getBounds())]
        ])
    })
}

function setGetParameter(params)
{
    var url = window.location.href;
    var hash = location.hash;
    url = url.replace(hash, '');

    for (i = 0; i < params.length; i++){
        if (url.indexOf(params[i][0] + "=") >= 0)
        {
            var prefix = url.substring(0, url.indexOf(params[i][0] + "=")); 
            var suffix = url.substring(url.indexOf(params[i][0] + "="));
            suffix = suffix.substring(suffix.indexOf("=") + 1);
            suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
            url = prefix + params[i][0] + "=" + params[i][1] + suffix;
        }
        else
        {
            if (url.indexOf("?") < 0)
                url += "?" + params[i][0] + "=" + params[i][1];
            else
                url += "&" + params[i][0] + "=" + params[i][1];
        }
    }
    

    window.history.pushState("", "", url + hash);
}









/*

mapViewPage = {
    options: {
        mapViewContainerId: '',
        accomodationOfferURL : '',
        transportationOfferURL : '',
        translationOfferURL : '',
        genericOfferURL : '',
        supporterListURL  : '',
        mapboxToken: '',
        isStudent: true,
        isHospital: true,
        createPopupTextTransportation  :  (countrycode,city, plz, count, url) => '',
        createPopupTextGeneric  :  (countrycode,city, plz, count, url) => '',
        createPopupTextTranslation :  (countrycode,city, plz, count, url) => '',
        createPopupTextAccomodation :  (countrycode,city, plz, count, url) => '',
        createAccomodationCountText: (count) => '',
        createTransportationCountText: (count) => '',
        createTranslationCountText: (count) => '',
        createDigitalCountText: (count) => '',
        createGenericCountText: (count) => '',
        startPosition: '',
        facilityIcon: new L.Icon.Default(),

    },

    mapObject: null,
       
    createGenericIcon: function createGenericIcon(count) {
        return L.divIcon({
            className: 'leaflet-marker-icon marker-cluster marker-cluster-single leaflet-zoom-animated leaflet-interactive genericMarker',
            html: `<div><span>${count}</span></div>`,
            iconSize: [40, 40],
            popupAnchor: [-10,-10],
        })
    },
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


    initializeMap:  function initializeMap() {
       
        let mapOptions = {
            center: this.options.startPosition,
            zoom: this.options.zoom
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
// @todo : Optimize this logic to only gather those Offer types that are requested..
    loadMapMarkers : async function loadMapMarkers() {
        let [ accomodations, transportations, translations, generic ] = await Promise.all([$.get(this.options.accomodationOfferURL),$.get(this.options.transportationOfferURL),$.get(this.options.translationOfferURL),$.get(this.options.genericOfferURL)])
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
        
        // GENERIC:
        var genericClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('genericMarker'),
        });
        let genericMarkers = L.featureGroup.subGroup(genericClusterMarkerGroup, this.createMapMarkers(generic,(lat,lon,countrycode,city,plz,count) => {
            return L.marker([lon,lat],{ 
                icon:  this.createGenericIcon(count),
                itemCount: count,
           }).bindPopup(this.options.createPopupTextGeneric(countrycode,city, plz, count, this.options.genericOfferURL.replace("COUNTRYCODE",countrycode).replace("PLZ",plz)))
        }))

        
        var overlays = {}

        const countItems = (o) => {
            var count = 0
            for (countryCode in o) {
                for (zipCode in o[countryCode]) {
                    count += o[countryCode][zipCode].count
                }
            }
            return count
        }

        {%if translation  %}
        translationClusterMarkerGroup.addTo(this.mapObject)
        translationMarkers.addTo(this.mapObject)
        overlays[this.options.createTranslationCountText(countItems(translations))] = translationMarkers
        {% endif %}
        {%if transportation  %}
        transportationClusterMarkerGroup.addTo(this.mapObject)
        transportationMarkers.addTo(this.mapObject)
        overlays[this.options.createTransportationCountText(countItems(transportations))] = transportationMarkers
        {% endif %}
        {%if accomodation  %}
        accomodationClusterMarkerGroup.addTo(this.mapObject)
        accomodationMarkers.addTo(this.mapObject)
        overlays[this.options.createAccomodationCountText(countItems(accomodations))] = accomodationMarkers
        {% endif %}
        {%if generic  %}
        genericClusterMarkerGroup.addTo(this.mapObject)
        genericMarkers.addTo(this.mapObject)
        overlays[this.options.createGenericCountText(countItems(generic))] = genericMarkers
        {% endif %}
        


        control = L.control.layers(null, overlays, { collapsed: false, position: 'topright' }).addTo(this.mapObject)
        var htmlObject = control.getContainer();
        // Get the desired parent node.
        var a = document.getElementById('controlContainer');

        // Finally append that node to the new parent, recursively searching out and re-parenting nodes.
        function setParent(el, newParent)
        {
            newParent.appendChild(el);
        }
        setParent(htmlObject, a);

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

})*/