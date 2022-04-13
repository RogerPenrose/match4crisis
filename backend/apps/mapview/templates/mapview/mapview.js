mapViewPage = {
    options: {
        mapViewContainerId: '',
        accommodationOfferURL : '',
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
        createPopupTextAccommodation :  (countrycode,city, plz, count, url) => '',
        createAccommodationCountText: (count) => '',
        createTransportationCountText: (count) => '',
        createTranslationCountText: (count) => '',
        createDigitalCountText: (count) => '',
        createGenericCountText: (count) => '',
        startPosition: '',
        facilityIcon: new L.Icon.Default(),

    },

    mapObject: null,
    
    createIcon: function createIcon(count, className) {
        return L.divIcon({
            className: `leaflet-marker-icon marker-cluster marker-cluster-single leaflet-zoom-animated leaflet-interactive ${ className }`,
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


    initializeMap:  function initializeMap() {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
    
        getParamUrlCenter = [Number(urlParams.get('lat')), Number(urlParams.get('lng'))]

        let mapOptions;
        
        if (typeof getParamUrlCenter[0] === "number" && typeof getParamUrlCenter[1] === "number") {
            mapOptions = {
                center: getParamUrlCenter,
                zoom: this.options.zoom
            }
        } else {
            mapOptions = {
                center: this.options.startPosition,
                zoom: this.options.zoom
            }
        }

        let tileLayerURL = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}@2x?access_token=' + this.options.mapboxToken
        let tileLayerOptions = {
            attribution: ' <a href="https://www.mapbox.com/about/maps/">© Mapbox</a> | <a href="http://www.openstreetmap.org/copyright">© OpenStreetMap</a> | <a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>',
            maxZoom: 18,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            preferCanvas: true
          }
    
        this.mapObject = L.map(this.options.mapViewContainerId,mapOptions);

        const bb = urlParams.get('bb')
        if (bb){
            try {
                const vp = JSON.parse(bb);
                mapViewPage.mapObject.fitBounds(new L.latLngBounds([[vp.south, vp.west], [vp.north, vp.east]]));
            } catch(e){
                console.log("Url_param bb is damaged!")
                mapViewPage.mapObject.fitBounds(new L.latLngBounds([[49.27, 7.86], [53.1, 13.04]]));
            }
        } else {
            mapViewPage.mapObject.fitBounds(new L.latLngBounds([[49.27, 7.86], [53.1, 13.04]]));
        }

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
        let [ accommodations, transportations, translations, generic ] = await Promise.all([$.get(this.options.accommodationOfferURL),$.get(this.options.transportationOfferURL),$.get(this.options.translationOfferURL),$.get(this.options.genericOfferURL)])
          // ACCOMMODATIONS:
        var accommodationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('accommodationMarker'),
        });
        let accommodationMarkers = L.featureGroup.subGroup(accommodationClusterMarkerGroup, this.createMapMarkers(accommodations,(lat,lon,location,descr,refer_url) => {
            return L.marker([lon,lat],{ 
                icon:  this.createIcon(1, "accommodationMarker"),
                itemCount: 1,
           }).bindPopup(this.options.createPopupTextAccommodation(descr, location, refer_url))
        }))
        // TRANSPORTATIONS:

        var transportationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('transportationMarker'),
        });
        var transportationMarkers = L.featureGroup.subGroup(transportationClusterMarkerGroup, this.createMapMarkers(transportations,(lat,lon,location,descr,refer_url) => {
            return L.marker([lon,lat],{
                 icon:  this.createIcon(1, "transportationMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextTransportation(descr, location, refer_url))
        }))

        // TRANSLATIONS:
       
        var translationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('translationMarker'),
        });
        var translationMarkers = L.featureGroup.subGroup(translationClusterMarkerGroup, this.createMapMarkers(translations,(lat,lon,location,descr,refer_url) => {
            return L.marker([lon,lat],{
                 icon:  this.createIcon(1, "translationMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextTranslation(descr, location, refer_url))
        }))
        
        // GENERIC:
        var genericClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('genericMarker'),
        });
        let genericMarkers = L.featureGroup.subGroup(genericClusterMarkerGroup, this.createMapMarkers(generic,(lat,lon,location,descr,refer_url) => {
            return L.marker([lon,lat],{ 
                icon:  this.createIcon(1, "genericMarker"),
                itemCount: 1,
           }).bindPopup(this.options.createPopupTextGeneric(descr, location, refer_url))
        }))

        /*var checks = document.querySelectorAll('[type = "checkbox"]'), i;
        function disCheck() {
            for (i = 0; i < checks.length; ++i) {
                checks[i].disabled = true;*/

                
        var overlays = {}

        translationClusterMarkerGroup.addTo(this.mapObject)
        translationMarkers.addTo(this.mapObject)
        overlays[this.options.createTranslationCountText(translations.length)] = translationMarkers

        transportationClusterMarkerGroup.addTo(this.mapObject)
        transportationMarkers.addTo(this.mapObject)
        overlays[this.options.createTransportationCountText(transportations.length)] = transportationMarkers

        accommodationClusterMarkerGroup.addTo(this.mapObject)
        accommodationMarkers.addTo(this.mapObject)
        overlays[this.options.createAccommodationCountText(accommodations.length)] = accommodationMarkers

        genericClusterMarkerGroup.addTo(this.mapObject)
        genericMarkers.addTo(this.mapObject)
        overlays[this.options.createGenericCountText(generic.length)] = genericMarkers

        const control = L.control.layers(null, overlays, { collapsed: false, position: 'topright' }).addTo(this.mapObject)
        const htmlObject = control.getContainer();
        // Get the desired parent node.
        const a = document.getElementById('controlContainer');

        // Finally append that node to the new parent, recursively searching out and re-parenting nodes.
        function setParent(el, newParent)
        {
            newParent.appendChild(el);
        }
        setParent(htmlObject, a);

        
        // click (uncheck) checkboxes, if not selected in URL-Params
        const checkboxes_to_disable = [
            "{{ translation }}",
            "{{ transportation }}",
            "{{ accommodation }}",
            "{{ generic }}"
        ].map(b => b == "True")

        const offersCheckboxParents = document.getElementById("controlContainer")
                                    .childNodes[0]
                                    .childNodes[1]
                                    .childNodes[2]
                                    .childNodes

        for (i in checkboxes_to_disable){
            if (!checkboxes_to_disable[i]) offersCheckboxParents[i].childNodes[0].childNodes[0].click();
        }
    },

    createMapMarkers : function addMapMarkers(markers, createMarkerFunction) {
        return markers.map(marker => {
            return createMarkerFunction(marker.lng, marker.lat, marker.offerDescription, marker.location, marker.refer_url)
        })
    },

    initAutocomplete: () => {
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
            
            const lat = place.geometry.location.lat()
            const lng = place.geometry.location.lng()

            if (place.geometry.viewport) {
                const vp = place.geometry.viewport
                mapViewPage.mapObject.fitBounds(new L.latLngBounds([[vp.zb.h, vp.Ua.h], [vp.zb.j, vp.Ua.j]]));
                mapViewPage.setGetParameter([
                    ["location", input.value], 
                    ["lat", lat], 
                    ["lng", lng], 
                    ["bb", JSON.stringify(place.geometry.viewport)]
                ])
            } else {
                mapViewPage.mapObject.setView(new L.LatLng(lat, lng), 15);
                mapViewPage.setGetParameter([
                    ["location", input.value], 
                    ["lat", lat], 
                    ["lng", lng], 
                ])
            }        
        });
    
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
    
        loc = urlParams.get('location')
        if (loc) {
            input.setAttribute("value", loc);
        }

        update_link_params = [];
        ["lat", "lng", "bb", "location"].forEach(p => {
            if (urlParams.get(p)){
                update_link_params.push([p, urlParams.get(p)])
            }
        });

        mapViewPage.update_link_element_params(update_link_params);
    },

    setGetParameter: function setGetParameter(params)
        {
            var url = window.location.href.split("#")[0];
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

            this.update_link_element_params(params);
        },

    update_link_element_params : params => ["results_as_list", "nav-link_search", "nav-link_map"].forEach(id => {
        upadateLinksElementParams(
            document.getElementById(id),
            params
        )
    })
}
$.extend(mapViewPage.options, pageOptions)

document.addEventListener("DOMContentLoaded", function domReady() {

    mapViewPage.initializeMap()
    mapViewPage.loadMapMarkers()
    mapViewPage.registerEventHandlers(document, window)

})