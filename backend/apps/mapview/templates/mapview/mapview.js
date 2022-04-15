mapViewPage = {
    options: {
        mapViewContainerId: '',
        accommodationOfferURL : '',
        jobOfferURL : '',
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
        createPopupTextAccommodation :  (descr, location,type, numberOfAdults, numberOfChildren, numberOfPets, refer_url) => '',
        createAccommodationCountText: (count) => '',
        createTransportationCountText: (count) => '',
        createTranslationCountText: (count) => '',
        createDigitalCountText: (count) => '',
        createGenericCountText: (count) => '',
        startPosition: '',
        facilityIcon: new L.Icon.Default(),

    },

    offers: [
        {
            type: "childcare",
            amt: Number("{{ entryCount.childcare }}"),
            show: "{{ childcare|default:False }}".toLowerCase() == "true"
        },{
            type: "manpower",
            amt: Number("{{ entryCount.manpower }}"),
            show: "{{ manpower|default:False }}".toLowerCase() == "true"
        },{
            type: "job",
            amt: Number("{{ entryCount.job }}"),
            show: "{{ job|default:False }}".toLowerCase() == "true"
        },{
            type: "buerocratic",
            amt: Number("{{ entryCount.buerocratic }}"),
            show: "{{ buerocratic|default:False }}".toLowerCase() == "true"
        },{
            type: "medical",
            amt: Number("{{ entryCount.medical }}"),
            show: "{{ medical|default:False }}".toLowerCase() == "true"
        },{
            type: "translation",
            amt: Number("{{ entryCount.translation }}"),
            show: "{{ translation|default:False }}".toLowerCase() == "true"
        },{
            type: "transportation",
            amt: Number("{{ entryCount.transportation }}"),
            show: "{{ transportation|default:False }}".toLowerCase() == "true"
        },{
            type: "accommodation",
            amt: Number("{{ entryCount.accommodation }}"),
            show: "{{ accommodation|default:False }}".toLowerCase() == "true"
        },{
            type: "generic",
            amt: Number("{{ entryCount.generic }}"),
            show: "{{ generic|default:False }}".toLowerCase() == "true"
        }
    ],

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
        const [ manpowers, childcares,medicals,buerocratics,jobs,accommodations, transportations, translations ] = await Promise.all([$.get(this.options.manpowerOfferURL),$.get(this.options.childcareOfferURL),$.get(this.options.medicalOfferURL),$.get(this.options.buerocraticOfferURL),$.get(this.options.jobOfferURL),$.get(this.options.accommodationOfferURL),$.get(this.options.transportationOfferURL),$.get(this.options.translationOfferURL)])
        const generic = [] // we could remove that from lelfeat, since we only need it to activate / deactivate the others but it is easier to deal with it that way
        
        // ACCOMMODATIONS:
        var accommodationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('accommodationMarker'),
        });
        let accommodationMarkers = L.featureGroup.subGroup(accommodationClusterMarkerGroup, this.createBlankMapMarker(accommodations,(marker) => {
            return L.marker([marker.lat,marker.lng],{ 
                icon:  this.createIcon(1, "accommodationMarker"),
                itemCount: 1,
           }).bindPopup(this.options.createPopupTextAccommodation(marker))
        }))
        // TRANSPORTATIONS:

        var transportationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('transportationMarker'),
        });
        var transportationMarkers = L.featureGroup.subGroup(transportationClusterMarkerGroup, this.createBlankMapMarker(transportations,(marker) => {
            return L.marker([marker.lat,marker.lng],{
                 icon:  this.createIcon(1, "transportationMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextTransportation(marker))
        }))

        // TRANSLATIONS:
       
        var translationClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('translationMarker'),
        });
        var translationMarkers = L.featureGroup.subGroup(translationClusterMarkerGroup, this.createBlankMapMarker(translations,(marker) => {
            return L.marker([marker.lat,marker.lng],{
                 icon:  this.createIcon(1, "translationMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextTranslation(marker))
        }))
        
        // BUEROCRATIC:
       
        var buerocraticClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('buerocraticMarker'),
        });
        var buerocraticMarkers = L.featureGroup.subGroup(buerocraticClusterMarkerGroup, this.createBlankMapMarker(buerocratics,(marker) => {
            return L.marker([marker.lat,marker.lng],{
                 icon:  this.createIcon(1, "buerocraticMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextBuerocratic(marker))
        }))
        // JOBS:
       
        var jobClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('jobMarker'),
        });
        var jobMarkers = L.featureGroup.subGroup(jobClusterMarkerGroup, this.createBlankMapMarker(jobs,(marker) => {
            return L.marker([marker.lat,marker.lng],{
                 icon:  this.createIcon(1, "jobMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextJob(marker))
        }))
        // MANPOWER:
       
        var manpowerClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('manpowerMarker'),
        });
        var manpowerMarkers = L.featureGroup.subGroup(manpowerClusterMarkerGroup, this.createBlankMapMarker(manpowers,(marker) => {
            return L.marker([marker.lat,marker.lng],{
                 icon:  this.createIcon(1, "manpowerMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextManpower(marker))
        }))
        // MEDICAL:
       
        var medicalClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('medicalMarker'),
        });
        var medicalMarkers = L.featureGroup.subGroup(medicalClusterMarkerGroup, this.createBlankMapMarker(medicals,(marker) => {
            return L.marker([marker.lat,marker.lng],{
                 icon:  this.createIcon(1, "medicalMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextMedical(marker))
        }))
        
        // CHILDCARE:
       
        var childcareClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('childcareMarker'),
        });
        var childcareMarkers = L.featureGroup.subGroup(childcareClusterMarkerGroup, this.createBlankMapMarker(childcares,(marker) => {
            return L.marker([marker.lat,marker.lng],{
                 icon:  this.createIcon(1, "childcareMarker"),
                 itemCount: 1,
            }).bindPopup(this.options.createPopupTextChildcare(marker))
        }))
        
        // GENERIC:  // somewhat redundant
        var genericClusterMarkerGroup = L.markerClusterGroup({
            iconCreateFunction: this.cssClassedIconCreateFunction('genericMarker'),
        });
        let genericMarkers = L.featureGroup.subGroup(genericClusterMarkerGroup, this.createGenericMapMarkers(generic,(lat,lon,location,descr,refer_url) => {
            return L.marker([lon,lat],{ 
                icon:  this.createIcon(1, "genericMarker"),
                itemCount: 1,
           }).bindPopup(this.options.createPopupTextGeneric(descr, location, refer_url))
        }))
                
        var overlays = {}
        
        childcareClusterMarkerGroup.addTo(this.mapObject)
        childcareMarkers.addTo(this.mapObject)
        overlays[this.options.createChildcareCountText(childcares.length)] = childcareMarkers

        manpowerClusterMarkerGroup.addTo(this.mapObject)
        manpowerMarkers.addTo(this.mapObject)
        overlays[this.options.createManpowerCountText(manpowers.length)] = manpowerMarkers

        jobClusterMarkerGroup.addTo(this.mapObject)
        jobMarkers.addTo(this.mapObject)
        overlays[this.options.createJobCountText(jobs.length)] = jobMarkers

        buerocraticClusterMarkerGroup.addTo(this.mapObject)
        buerocraticMarkers.addTo(this.mapObject)
        overlays[this.options.createBuerocraticCountText(buerocratics.length)] = buerocraticMarkers

        medicalClusterMarkerGroup.addTo(this.mapObject)
        medicalMarkers.addTo(this.mapObject)
        overlays[this.options.createMedicalCountText(medicals.length)] = medicalMarkers

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

        const offersCheckboxParents = document.getElementById("controlContainer")
                                    .childNodes[0]
                                    .childNodes[1]
                                    .childNodes[2]
                                    .childNodes;

        for (const i in this.offers){
            if (i != 8){
                this.offers[i].el = offersCheckboxParents[i].childNodes[0].childNodes[0]
                this.offers[i].el.setAttribute("name", this.offers[i].type);
                this.offers[i].el.addEventListener("change", e => this.handleCheckBoxClick(e));
                if (!this.offers[i].show) {
                    this.offers[i].show = true; // because it gets flipped in next line
                    this.offers[i].el.click();
                } else {
                    this.setGetParameter([[this.offers[i].type, "True"]])
                }
            } else {
                this.offers[i].el = offersCheckboxParents[i].childNodes[0].childNodes[0]
                this.offers[i].el.setAttribute("name", this.offers[i].type);
                if (!this.offers[i].show) {
                    this.offers[i].show = true; // because it gets flipped in next line
                    this.offers[i].el.click();
                } else {
                    this.setGetParameter([[this.offers[i].type, "True"]])
                }
                this.offers[i].el.addEventListener("change", e => this.handleCheckBoxClick(e));
                if (this.offers.findIndex((el) => el.show) == 8){
                    this.offers[i].el.click();
                    this.offers[i].el.click();
                }
            }
        }
    },

    handleCheckBoxClick: (e) => {
        if (e.target.name === "generic"){
            if (!mapViewPage.offers[8].show){
                mapViewPage.offers[8].show = true;
                mapViewPage.setGetParameter([["generic", "True"]])
                mapViewPage.offers.forEach(el => {
                    if (el.type !== "generic" && !el.show){
                        el.el.click();
                    }
                });
            }
            
            // aktiv und nicht alle ausgewählt
            else if (mapViewPage.offers.findIndex(el => !el.show) !== -1){
                mapViewPage.offers[8].show = false;
                mapViewPage.setGetParameter([["generic", "False"]])
                e.target.click();
                return;
            }

            // aktiv und alle ausgewählt
            else {
                mapViewPage.offers[8].show = false;
                mapViewPage.setGetParameter([["generic", "False"]])
                mapViewPage.offers.forEach(el => {
                    if (el.type !== "generic"){
                        el.el.click();
                    }
                });
            }
        } else {
            const index = mapViewPage.offers.findIndex(el => el.type == e.target.name);
            mapViewPage.offers[index].show = !mapViewPage.offers[index].show;
            mapViewPage.setGetParameter([[e.target.name, mapViewPage.offers[index].show]])
 
            // is not all are selected anymore
            /* if (mapViewPage.offers.findIndex(el => !el.show) !== -1 && mapViewPage.offers[8].show){
                mapViewPage.offers[8].el.click()
            }*/
        }
        mapViewPage.updateViewAsListBtn();
    },

    createGenericMapMarkers : function addMapMarkers(markers, createMarkerFunction) {
        return markers.map(marker => {
            return createMarkerFunction(marker.lng, marker.lat, marker.offerDescription, marker.location, marker.refer_url)
        })
    },
    createBlankMapMarker: function addMapMarkers(markers, createMarkerFunction){
        return markers.map(marker => {return createMarkerFunction(marker)})
    },
    updateViewAsListBtn: () => {
        document.getElementById("resultString").textContent = mapViewPage.offers.reduce((total, offer) => total + offer.show * offer.amt, 0)
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

function handleNumber(name, state){
    // console.log("Handling: "+name)
    number = 0
    checkAll = false
    link = "/offers/handle_filter?show_list=True&"
    
    try{
    if(window.document.getElementsByName("generic")[0].checked == true && name != "generic" && state == true)
            window.document.getElementsByName("generic")[0].click()
    }catch (e){

    }
    finally{
        
        for (var i = 0; i < checkboxes_to_disable.length; i++)
        {
            checkbox = checkboxes_to_disable[i]
            if (checkbox.type == name){
                checkboxes_to_disable[i].selected = state
                // console.log("New State: "+checkboxes_to_disable[i].selected)
            
            }
            if (checkboxes_to_disable[i].selected == true && checkboxes_to_disable[i].type != "generic"){
                // console.log("Adding : "+checkboxes_to_disable[i].type)
                number += eval(checkboxes_to_disable[i].type)
                if (checkboxes_to_disable[i].type != "childcare")
                    link +=checkboxes_to_disable[i].type+"Visible=True&"
                else link += "childShortVisible=True&childLongVisible=True&"
            }
            if (checkboxes_to_disable[i].selected == true && checkboxes_to_disable[i].type == "generic"){
                checkAll = true
            }

        }
        if (checkAll){
            number = 0
            link = "/offers/handle_filter?show_list=True&"
        for(var i = 0; i < checkboxes_to_disable.length; i++)
        {   if(checkboxes_to_disable[i].type != "generic"){
                number += eval(checkboxes_to_disable[i].type)
            if (checkboxes_to_disable[i].type != "childcare")
                link +=checkboxes_to_disable[i].type+"Visible=True"
            else link += "childShortVisible=True&childLongVisible=True&"

        }
            }
        }
        // console.log("States: "+JSON.stringify(checkboxes_to_disable))
        // console.log("New number: "+number)
        
        document.getElementById("results_as_list").href = link.slice(0,-1)
        document.getElementById("resultString").innerHTML = number
    }
}

document.addEventListener("DOMContentLoaded", function domReady() {

    mapViewPage.initializeMap()
    mapViewPage.loadMapMarkers()
    mapViewPage.registerEventHandlers(document, window)

})