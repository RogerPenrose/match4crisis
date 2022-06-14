function offer_autocomplete(){
    function getInputs(list){
        const inputs = []
        for(var i = 0; i < list.length; i++){
            const input = document.getElementById(list[i].name)
            if (input != null && input.nodeName == "INPUT"){
                console.log("Hit for "+list[i])
                inputs.push({
                    "input": input, 
                    "latNames": list[i].latNames, 
                    "bbNames": list[i].bbNames, 
                    "lngNames": list[i].lngNames
                })
            }
        }
        return inputs
    }

    const autocompletes = []
    const inputIDList = [
        {name: "id_location", latNames: ["lat", "id_lat"], lngNames: ["lng", "id_lng"], bbNames : ["bb", "id_bb"]},
        {name: "id_locationEnd", latNames: ["latEnd", "id_latEnd"], lngNames: ["lngEnd", "id_lngEnd"], bbNames : ["bbEnd", "id_bbEnd"]},
        {name: "location", latNames: ["lat"], lngNames: ["lng"], bbNames : ["bb"]}
    ]
    const inputs = getInputs(inputIDList)
    for(var i = 0; i < inputs.length; i++){
        const input = inputs[i].input;
        const latNames = inputs[i].latNames;
        const bbNames = inputs[i].bbNames;
        const lngNames = inputs[i].lngNames;

        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);

        const loc = urlParams.get('location')
        if (loc) {
            input.setAttribute("value", loc)
        }

        const autocomplete = new google.maps.places.Autocomplete(input, {
            type:"geocode"
        });
        autocomplete.inputId = input.id;

        autocomplete.setComponentRestrictions({
            // EU-countries + EFTA-countries + UK
            country: ["be", "bg", "cz", "dk", "de", "ee", "ie", "el", "es", "fr", "hr", "it", "cy", "lv", "lt", "lu", "hu", "mt", "nl", "at", "pl", "pt", "ro", "si", "sk", "fi", "se",    "is", "no", "ch", "li", "uk"],
        });   
        autocomplete.addListener("place_changed", () => {
            const place = autocomplete.getPlace();
            latNames.forEach(n => {
                lat = document.getElementsByName(n)[0]
                if (lat) lat.value = place.geometry.location.lat()
            })
            lngNames.forEach(n => {
                lng = document.getElementsByName(n)[0]
                if (lng) lng.value = place.geometry.location.lng()
            })
            
            if (place.geometry.viewport){
                bbNames.forEach(n => {
                    bb = document.getElementsByName(n)[0]
                    if (bb) bb.value = JSON.stringify(place.geometry.viewport)
                })
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
            // values / elements not given || we are not at transportation_offers
        }

        autocompletes.push(autocomplete);
    }
    return autocompletes
}

/**
 * Binds an action to a checkbox to show/hide another field.
 * @param checkbox The id of the Checkbox that toggles if the other field is displayed
 * @param toggled The id of the field that is toggled by the checkbox  
 * @param reverse If true `toggled` will hide when `checkbox` is checked and vice versa
 */
function bindCheckboxToggle(checkbox, toggled, reverse=false){
    $(`#id_${checkbox}`).on('change', function() {
        if (this.checked != reverse) {
            $(`#div_id_${toggled}`).show()
        } else {
            $(`#div_id_${toggled}`).hide()
        }
    }).change()
}

/**
 * Binds an action to a select to show/hide another field depending on which option is chosen
 * @param select The id of the Select that toggles if the other field is displayed
 * @param value If this is chosen `toggled` will be shown, otherwise hidden
 * @param toggled The id of the field that is toggled by the select  
 */
function bindSelectToggle(select, value, toggled){
    $(`#id_${select}`).on('change', function() {
        if (this.value == value) {
            $(`#div_id_${toggled}`).show()
        } else {
            $(`#div_id_${toggled}`).hide()
        }
    }).change()
}

function save_without_active(){
    var form = $("#offerForm")
    var pathArray = window.location.pathname.split('/');
    form.attr('action', pathArray[pathArray.length - 1] === "edit" ? ("/offers/" + pathArray[pathArray.length - 2] + "/save") : "/offers/save");
    form.submit();
}
