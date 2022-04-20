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

function validateForm(){
    let allAreFilled = true;
    document.getElementById("thisForm").querySelectorAll("[required]").forEach(function(i) {
      if (!allAreFilled) return;
      if (i.type === "radio") {
        let at_least_one_filled = false;
        document.getElementById("thisForm").querySelectorAll(`[name=${i.name}]`).forEach(function(r) {
            at_least_one_filled = at_least_one_filled || r.checked;
        })
        allAreFilled = allAreFilled && at_least_one_filled;
      } else {
        allAreFilled = allAreFilled && i.value;
      }
  });
  return allAreFilled;
}

function save_without_active(){
    var checkbox= document.getElementById("id_active")
    checkbox.checked = false
    var form = document.getElementById("thisForm");
    var pathArray = window.location.pathname.split('/');
    if(pathArray[pathArray.length - 1] === "edit"){
        form.action = "/offers/" + pathArray[pathArray.length - 2] + "/save";
    }else{
        form.action = "/offers/save";
    }
    form.submit();
}

function save_with_active(){
    var checkbox= document.getElementById("id_active")
    checkbox.checked = true
    var form = document.getElementById("thisForm");
    var pathArray = window.location.pathname.split('/');
    if(pathArray[pathArray.length - 1] === "edit"){
        form.action = "/offers/" + pathArray[pathArray.length - 2] + "/edit";
    }else{
        form.action = "/offers/createOffer";
    }
    // if(validateForm()){
    //     form.submit();
    // }
}