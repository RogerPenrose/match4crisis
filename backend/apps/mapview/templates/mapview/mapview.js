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
    markerIcons : {},
    
    createIcon: function createIcon(iconContent, className) {
        return L.divIcon({
            className: `leaflet-marker-icon marker-cluster marker-cluster-single leaflet-zoom-animated leaflet-interactive ${ className }`,
            html: `<div><span>${iconContent}</span></div>`,
            iconSize: [40, 40],
            popupAnchor: [0,-60],
        })
    },

    cssClassedIconCreateFunction: function cssClassedIconCreateFunction(cssClass) {
        return (function (cluster) {
            var childCount = cluster.getChildCount();
            var cssClasses = ['marker-cluster']
            cssClasses.push('marker-cluster-' + (childCount < 10 ? 'small' : (childCount < 100 ? 'medium' : 'large')))
            cssClasses.push(cssClass)
            return new L.DivIcon({
                 html: '<div><span>' + childCount + '</span></div>',
                 className: cssClasses.join(' '), 
                 iconSize: new L.Point(40, 40) 
            })
        })
    },


    initializeMap: function initializeMap() {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
    
        let mapOptions = {
                center: this.options.startPosition,
                zoom: this.options.zoom
            }

        let tileLayerURL = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}@2x?access_token=' + this.options.mapboxToken
        let tileLayerOptions = {
            attribution: ' <a href="https://www.mapbox.com/about/maps/">© Mapbox</a> | <a href="http://www.openstreetmap.org/copyright">© OpenStreetMap</a> | <a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>',
            maxZoom: 18,
            minZoom: 2,
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
            }
        }

        L.tileLayer(tileLayerURL, tileLayerOptions).addTo(this.mapObject);    

        // Enhance MarkerCluster - override getChildCount
        L.MarkerCluster.prototype.getChildCount = function (){
            const children = this.getAllChildMarkers()
            return children.reduce((sum,marker) => (sum + marker.options.itemCount),0)
        }

        $.get("/mapview/counts" + window.location.search, (counts, status) => {

            this.markerGroup = L.markerClusterGroup({
                iconCreateFunction: this.cssClassedIconCreateFunction(""),
            }).addTo(this.mapObject); 

            this.layers = this.createControlGroups(counts)            

            this.control = L.control.groupedLayers(null, this.layers, { collapsed: false, position: 'topright', groupCheckboxes: true}).addTo(this.mapObject)
            $("#controlContainer").append(this.control.getContainer())

            // Hide the empty group label
            for(const groupLabel of $(".leaflet-control-layers-group-label")){
                if(groupLabel.innerText===""){
                    groupLabel.style.display = "none"
                }
            }
        })


        this.mapObject.on('overlayadd', (e) => {
            this.loadMapMarkers(e.layer)
        })

    },

    createControlGroups: function createControlGroups(counts, parentLabel=""){
        const newLayer = {}
        for (let [entryType, entry] of Object.entries(counts)) {
            if(typeof entry !== 'object'){
                continue
            }
            if ("count" in entry){

                // var markerGroup = L.markerClusterGroup({
                //     iconCreateFunction: this.cssClassedIconCreateFunction(entryType),
                // });
                let markers = L.featureGroup.subGroup(this.markerGroup)
                markers.typeIdentifier = parentLabel + entryType

                if(entry['selected']){
                    this.loadMapMarkers(markers)
                    this.mapObject.addLayer(markers)
                }

                if(parentLabel){
                    newLayer[`${entry['label']} (${entry['count']})`] = markers
                }else{
                    if(!newLayer.hasOwnProperty("")){
                        newLayer[""] = {}
                    }
                    newLayer[""][`${entry['label']} (${entry['count']})`] = markers
                }

            }else{
                newLayer[`${entry['label']} (${entry['groupCount']})`] = this.createControlGroups(entry, entryType);
            }
        }
        return newLayer
    },

    loadMapMarkers : async function loadMapMarkers(layer){

        if(layer.loaded){
            return
        }
        
        const layerID = layer.typeIdentifier
        const data = await $.get("data?type=" + layerID)
        

        if(layerID in this.markerIcons){
            var svgIcon = this.markerIcons[layerID]
        }else{
            var svgIcon = await $.get(data['iconSrc'])
            this.markerIcons[layerID] = svgIcon
        }

        for(const k of data['entries']){
            layer.addLayer(L.marker([k['lat'], k['lng']], { 
                icon:  this.createIcon(svgIcon.documentElement.outerHTML, layer.typeIdentifier + "Marker"),
                itemCount: 1,
            }).bindPopup(k['popupContent']))
        }

        layer.loaded = true
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

    createBlankMapMarker: function addMapMarkers(markers, createMarkerFunction){
        return markers.map(marker => {return createMarkerFunction(marker)})
    },
    updateViewAsListBtn: () => {
        var count =  mapViewPage.offers.reduce((total, offer) => total + offer.show * offer.amt, 0)+mapViewPage.requests.reduce((total, request) => total + request.show * request.amt, 0)
       var possibleCount = mapViewPage.offers.reduce((total, offer) => total + offer.amt, 0)+mapViewPage.requests.reduce((total, request) => total + request.amt, 0)
       
       document.getElementById("resultString").textContent = count
        if (possibleCount == 0){
            document.getElementById("results_as_list").style.display = "none"
            console.log("No offers.")
            document.getElementById("no-offers").style.display = "initial"
        }
        else {
            document.getElementById("results_as_list").style.display = "initial"
            document.getElementById("no-offers").style.display = "none"

        }
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
                const vp = Object.values(place.geometry.viewport)

                mapViewPage.mapObject.fitBounds([[vp[0].h, vp[1].h], [vp[0].j, vp[1].j]]);
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

            // Source: https://stackoverflow.com/questions/5999118/how-can-i-add-or-update-a-query-string-parameter
            if ('URLSearchParams' in window) {
                var searchParams = new URLSearchParams(window.location.search)
                searchParams.set("foo", "bar"); // TODO
                var newRelativePathQuery = window.location.pathname + '?' + searchParams.toString();
                history.pushState(null, '', newRelativePathQuery);
            }

            // this.update_link_element_params(params);
        },

    update_link_element_params : params => ["results_as_list"/*, "nav-link_search", "nav-link_map"*/].forEach(id => { 
        upadateLinksElementParams(
            document.getElementById(id),
            params
        )
    })
}
$.extend(mapViewPage.options, pageOptions)

document.addEventListener("DOMContentLoaded", function domReady() {
    mapViewPage.initializeMap()
    mapViewPage.registerEventHandlers(document, window)
    
})