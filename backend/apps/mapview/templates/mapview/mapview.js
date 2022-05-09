mapViewPage = {
    options: {
        mapViewContainerId: '',
        mapboxToken: '',
        isStudent: true,
        isHospital: true, 
        startPosition: '',
        facilityIcon: new L.Icon.Default(),

    },
    requests: [],
    offers: [],
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
        
        if (!isNaN(getParamUrlCenter[0]) && !isNaN(getParamUrlCenter[1])) {
            mapOptions = {
                center: getParamUrlCenter,
                zoom: this.options.zoom
            }
        } else {
            this.setGetParameter([["lng", this.options.startPosition[0]], ["lat", this.options.startPosition[1]]])
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
    
        this.mapObject = L.map(this.options.mapViewContainerId, mapOptions);
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
        //const  [ manpowers, childcares,medicals,buerocratics,jobs,accommodations, transportations, translations ] = await Promise.all([$.get(this.options.manpowerOfferURL),$.get(this.options.childcareOfferURL),$.get(this.options.medicalOfferURL),$.get(this.options.buerocraticOfferURL),$.get(this.options.jobOfferURL),$.get(this.options.accommodationOfferURL),$.get(this.options.transportationOfferURL),$.get(this.options.translationOfferURL)])
        const genericParameters = await $.get("/mapview/generalInformationJSON")
        const generic = [] // we could remove that from lelfeat, since we only need it to activate / deactivate the others but it is easier to deal with it that way
        var entries =[]
        entries =await Promise.all(
            [{% for entry in categories %}          $.get("{{entry}}"),          {%endfor%}]
           )
        var offerOverlays = {}
        var requestOverlays ={}
        var show = [{%for entry in show%} "{{entry}}",{%endfor%}]
        console.log(show)
        
        for (var i = 0; i < entries.length; i++){
            console.log("Entry: "+i)
            if (entries[i].offers.length > 0){
                var markerGroup= L.markerClusterGroup({
                    iconCreateFunction: this.cssClassedIconCreateFunction('accommodationMarker'),
                });
                let markers = L.featureGroup.subGroup(markerGroup, this.createBlankMapMarker(entries[i].offers,(marker) => {
                    return L.marker([marker.lat,marker.lng],{ 
                        icon:  this.createIcon(1, "accommodationMarker"),
                        itemCount: 1,
                }).bindPopup(marker.text)
                }))
                markerGroup.addTo(this.mapObject)
                markers.addTo(this.mapObject)
                offerOverlays[entries[i].legend+"("+entries[i].offers.length+")"] = markers
                
            if (show.includes(entries[i].type)){
                this.offers.push({"type":entries[i].type, "amt": entries[i].offers.length, "show": true})
            }
            else this.offers.push({"type":entries[i].type, "amt": entries[i].offers.length, "show": false})
        }
        if (entries[i].requests.length > 0){
            var requestMarkerGroup = L.markerClusterGroup({
                iconCreateFunction: this.cssClassedIconCreateFunction('request'),
            });
            let requestMarkers = L.featureGroup.subGroup(requestMarkerGroup, this.createBlankMapMarker(entries[i].requests,(marker) => {
                return L.marker([marker.lat,marker.lng],{ 
                    icon:  this.createIcon(1, "request"),
                    itemCount: 1,
               }).bindPopup(marker.text)
            }))
            requestMarkerGroup.addTo(this.mapObject)
            requestMarkers.addTo(this.mapObject)
            requestOverlays[entries[i].legend+"("+entries[i].requests.length+")"] = requestMarkers
            if (show.includes(entries[i].type)){
                this.requests.push({"type":entries[i].type, "amt": entries[i].requests.length, "show": true})
            }
            else this.requests.push({"type":entries[i].type, "amt": entries[i].requests.length, "show": false})
        }
    }
        var offerString = "Angebote ("+genericParameters.offerCount+")"
        var requestString = "Gesuche ("+genericParameters.requestCount+")"
        console.log(JSON.stringify(this.requests))
        var groupedOverlays ={}
        groupedOverlays[offerString] = offerOverlays
        groupedOverlays[requestString] = requestOverlays
        //const control = L.control.layers(baseLayer, offerOverlays, { collapsed: false, position: 'topright' }).addTo(this.mapObject)
        const control = L.control.groupedLayers(null, groupedOverlays, { collapsed: false, position: 'topright', groupCheckboxes: true}).addTo(this.mapObject)
        const htmlObject = control.getContainer();
        // Get the desired parent node.
        const a = document.getElementById('controlContainer');

        // Finally append that node to the new parent, recursively searching out and re-parenting nodes.
        function setParent(el, newParent)
        {
            newParent.appendChild(el);
        }
        setParent(htmlObject, a);

        
        var requestsCheckboxParents = []
        var offersCheckboxParents = []
        
        if (this.offers.length > 0){
        // click (uncheck) checkboxes, if not selected in URL-Params
        console.log("Showing Offers")
          offersCheckboxParents = document.getElementById("controlContainer")
                                    .childNodes[0]
                                    .childNodes[0]
                                    .childNodes[2]
                                    .childNodes[0]
                                    .childNodes;
                                    offersCheckboxParents[0].childNodes[0].setAttribute("name", "allOffers");
                                    offersCheckboxParents[0].childNodes[0].addEventListener("change", e => this.handleCheckBoxClick(e));
        }
        if (this.requests.length > 0){
            console.log("Showing Requests")
         requestsCheckboxParents = document.getElementById("controlContainer")
                                    .childNodes[0]
                                    .childNodes[0]
                                    .childNodes[2];
            if (this.offers.length > 0)
            requestsCheckboxParents = requestsCheckboxParents.childNodes[1].childNodes;
            else requestsCheckboxParents = requestsCheckboxParents.childNodes[0].childNodes;            
                        requestsCheckboxParents[0].childNodes[0].setAttribute("name", "allRequests");
                        requestsCheckboxParents[0].childNodes[0].addEventListener("change", e => this.handleCheckBoxClick(e));
                                }
        
        for (const i in this.offers){
            var index = Number(i) + 1
                this.offers[i].el = offersCheckboxParents[index].childNodes[0]

                this.offers[i].el.setAttribute("name", this.offers[i].type);
                this.offers[i].el.addEventListener("change", e => this.handleCheckBoxClick(e));
                if (!this.offers[i].show) {
                    this.offers[i].show = true; // because it gets flipped in next line
                    this.offers[i].el.click();
                } else {
                    console.log("Show Offer: "+this.offers[i].el.name)
                    this.setGetParameter([[this.offers[i].type+"OffersVisible", "True"]])
                }
        }for (const i in this.requests){
            var index = Number(i) + 1
                this.requests[i].el = requestsCheckboxParents[index].childNodes[0]

                this.requests[i].el.setAttribute("name", this.requests[i].type);
                this.requests[i].el.addEventListener("change", e => this.handleCheckBoxClick(e, false));
                if (!this.requests[i].show) {
                    this.requests[i].show = true; // because it gets flipped in next line
                    this.requests[i].el.click();
                } else {
                    console.log("Show Request: "+this.requests[i].el.name)
                    this.setGetParameter([[this.requests[i].type+"RequestsVisible", "True"]])
                }
        }
    },

    handleCheckBoxClick: (e, isOffer=true) => {
        if (e.target.name == "allOffers"){
            for (var i = 0; i < mapViewPage.offers.length; i++){
                var entry = mapViewPage.offers[i]
                entry.show = e.target.checked
                entry.el.checked = e.target.checked
                mapViewPage.setGetParameter([[entry.type+"OffersVisible", entry.show]])
            }
        }
        else if (e.target.name == "allRequests"){
            for (var i = 0; i < mapViewPage.requests.length; i++){
                var entry = mapViewPage.requests[i]
                entry.show = e.target.checked
                entry.el.checked = e.target.checked
                mapViewPage.setGetParameter([[entry.type+"RequestsVisible",entry.show]])
            }

        }
        else {
            if (isOffer){
                const index = mapViewPage.offers.findIndex(el => el.type == e.target.name);
                mapViewPage.offers[index].show = !mapViewPage.offers[index].show;
                mapViewPage.setGetParameter([[e.target.name+"OffersVisible", mapViewPage.offers[index].show]])
            }
            else {
                const index = mapViewPage.requests.findIndex(el => el.type == e.target.name);
                mapViewPage.requests[index].show = !mapViewPage.requests[index].show;
                mapViewPage.setGetParameter([[e.target.name+"RequestsVisible", mapViewPage.requests[index].show]])

            }
        }
        mapViewPage.updateViewAsListBtn();
    },

    createBlankMapMarker: function addMapMarkers(markers, createMarkerFunction){
        return markers.map(marker => {return createMarkerFunction(marker)})
    },
    updateViewAsListBtn: () => {
        document.getElementById("resultString").textContent = mapViewPage.offers.reduce((total, offer) => total + offer.show * offer.amt, 0)+mapViewPage.requests.reduce((total, request) => total + request.show * request.amt, 0)
    },
    initAutocomplete: () => {
        const input = document.getElementById("location");
    
        const autocomplete = initMapsAutocomplete();
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

                // seems like they changed vp param_names 
                // TODO: -> fix google maps import version to specific value when finished with developing
                try{
                    mapViewPage.mapObject.fitBounds(new L.latLngBounds([[vp.Ab.h, vp.Ua.h], [vp.Ab.j, vp.Ua.j]]));
                } catch(e){
                    mapViewPage.mapObject.fitBounds(new L.latLngBounds([[vp.zb.h, vp.Ua.h], [vp.zb.j, vp.Ua.j]]));
                }
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