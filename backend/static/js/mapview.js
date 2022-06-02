mapViewPage = {
    options: {
        mapViewContainerId: '',
        mapboxToken: '',
        startPosition: '',
        defaultStartPosition: [ 51.13, 10.018 ],
        defaultZoom: 6,
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
                 iconSize: [40, 40]
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
    },

    createControlGroups: function createControlGroups(counts, parentLabel=""){
        const newLayer = {}
        for (let [entryType, entry] of Object.entries(counts)) {
            if(typeof entry !== 'object'){
                continue
            }
            if ("count" in entry){
                let markers = L.featureGroup.subGroup(this.markerGroup)
                markers.typeIdentifier = parentLabel + entryType

                if(entry['selected']){
                    this.loadMapMarkers(markers)
                    this.mapObject.addLayer(markers)
                    $("#filter-card-" + markers.typeIdentifier).show()
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
        const urlParams = new URLSearchParams(window.location.search)
        urlParams.set('type', layerID)
        const data = await $.get("data?" + urlParams.toString())
        

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
        let footerHeight = $('.footer').innerHeight()
        let newHeight = height - navHeight - footerHeight
        $('#' + this.options.mapViewContainerId).height(newHeight)
        mapViewPage.mapObject.invalidateSize()
    },

    registerEventHandlers : function registerEventHandlers(window) {
        $(window).on("resize", (event) => { this.onResizeWindow() }).trigger("resize")

        this.mapObject.on('overlayadd', (e) => {
            this.loadMapMarkers(e.layer)

            $("#filter-card-" + e.layer.typeIdentifier).show()

            this.alterGetParameters({"selected" : e.layer.typeIdentifier}, alteringType='append')
        })

        this.mapObject.on('overlayremove', (e) => {
            let typeID = e.layer.typeIdentifier

            let queryParams = new URLSearchParams(window.location.search)
            let paramsToRemove = Array.from(queryParams.keys()).filter(k => {
                return k.indexOf(typeID) == 0;
            }).reduce((newData, k) => {
                newData[k] = queryParams.getAll(k);
                return newData;
            }, {});
            paramsToRemove['selected'] = typeID
            this.alterGetParameters(paramsToRemove, alteringType='delete')

            $("#filter-card-" + typeID).hide()
        })
    },

    initAutocomplete: function initAutocomplete() {
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

                this.mapObject.fitBounds([[vp[0].h, vp[1].h], [vp[0].j, vp[1].j]]);
                this.alterGetParameters({
                    "location": input.value, 
                    "lat" : lat,
                    "lng" : lng,
                    "bb" : JSON.stringify(place.geometry.viewport)
                })
            } else {
                this.mapObject.setView(new L.LatLng(lat, lng), 15);
                this.alterGetParameters({
                    "location": input.value, 
                    "lat" : lat,
                    "lng" : lng,
                })
            }        
        });
    },

    clearLocationSearch: function clearLocationSearch(){
        $('#location')[0].value="";
        this.alterGetParameters({
            "location": '', 
            "lat" : '',
            "lng" : '',
            "bb" :''
        }, alteringType='remove')

        this.mapObject.setView(this.options.defaultStartPosition, this.options.defaultZoom)
    },

    alterGetParameters: function alterGetParameters(params, alteringType="replace"){
        /** Altering types:
         *      replace/set: replace the current query string entries with the given new values if there are any.
         *      append/add: append the new key-value-pairs regardless of whether they already exist
         *      delete/remove: Removes the given key-value-pairs (!!! Doesn't work if there are multiple pairs with the same key !!!)
         */

            if ('URLSearchParams' in window) {
                var searchParams = new URLSearchParams(window.location.search)
                Object.entries(params).forEach(([key, val]) => {
                    switch (alteringType) {
                        case "replace":
                        case "set":
                            searchParams.set(key, val);
                            break;
                        case "append":
                        case "add":
                            searchParams.append(key, val);
                            break;
                        case "delete":
                        case "remove":
                            let keyEntries = searchParams.getAll(key)
                            searchParams.delete(key)
                            if(val != ''){
                                for(let curEntry of keyEntries){
                                    if(curEntry != val){
                                        searchParams.append(key, curEntry)
                                    }
                                }
                            }
                            break;
                    }
                })
                var newRelativePathQuery = window.location.pathname + '?' + searchParams.toString();
                history.pushState(null, '', newRelativePathQuery);

                viewInListButton = $("#results_as_list")[0]
                if(viewInListButton){
                    viewInListButton.href = viewInListButton.href.split("?")[0] + '?' + searchParams.toString();
                }
            }
        },
}

$.extend(mapViewPage.options, pageOptions)

document.addEventListener("DOMContentLoaded", function domReady() {
    mapViewPage.initializeMap()
    mapViewPage.registerEventHandlers(window)
})