function getInputs(list){
    var inputs = []
    for(var i = 0; i < list.length; i++){
        var input = document.getElementById(list[i].name)
        if (input != null && input.nodeName == "INPUT"){
            console.log("Hit for "+list[i])
            inputs.push({"input":input, "latName": list[i].latName, "bbName": list[i].bbName, "lngName": list[i].lngName})
        }
    }
    return inputs
}
function initMapsAutocomplete(){
    var autocompletes = []
    var inputList = [{name: "id_location", latName: "lat", lngName: "lng", bbName : "bb"}, {name: "location", latName: "lat", lngName: "lng", bbName : "bb"}, {name: "id_locationEnd", latName: "latEnd", lngName: "lngEnd", bbName : "bbEnd"}]
    var inputs = getInputs(inputList)
    for(var i = 0; i < inputs.length; i++){
        console.log("Hit")
        var input = inputs[i].input
        var latName = inputs[i].latName
        var bbName = inputs[i].bbName
        var lngName = inputs[i].lngName

        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);

        const loc = urlParams.get('location')
        if (loc) {
            input.setAttribute("value", loc)
        }

        var autocomplete = new google.maps.places.Autocomplete(input, {
            type:"geocode"
        });
        autocomplete.inputId = input.id;

        autocomplete.setComponentRestrictions({
            // EU-countries + EFTA-countries + UK
            country: ["be", "bg", "cz", "dk", "de", "ee", "ie", "el", "es", "fr", "hr", "it", "cy", "lv", "lt", "lu", "hu", "mt", "nl", "at", "pl", "pt", "ro", "si", "sk", "fi", "se",    "is", "no", "ch", "li", "uk"],
        });   
        autocomplete.addListener("place_changed", () => {
            try {
                const lat = document.getElementsByName(latName)[0];
                const lng = document.getElementsByName(lngName)[0];
                const bb = document.getElementsByName(bbName)[0];
                const place = autocomplete.getPlace();
                lat.value = place.geometry.location.lat();
                lng.value = place.geometry.location.lng();
                if (place.geometry.viewport){
                    bb.value = JSON.stringify(place.geometry.viewport)
                }
            } catch {
                console.log("ERROR")
                // either we on mapview_page or place not found or no geometry
            }
            input.focus();
        });

        try {
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
        
            loc = urlParams.get('location')
            if (loc) {
                input.setAttribute("value", loc)
            }

            document.getElementsByName(latName)[0].setAttribute("value", urlParams.get('lat'));
            document.getElementsByName(lngName)[0].setAttribute("value", urlParams.get('lng'));
            document.getElementsByName(bbName)[0].setAttribute("value", urlParams.get('bb'));
        } catch {
            // either we on mapview_page or just not given
        }

        autocompletes.push(autocomplete);
    }
    return autocompletes
}

function init_google_maps() {
    if (typeof initMap === "function") initMap() // we are at mapview
    else if (typeof mapViewPage === "object") mapViewPage.initAutocomplete() // we are at /offers
    else initMapsAutocomplete();
}