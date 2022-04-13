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

function offer_autocomplete(){
    const autocompletes = []
    const inputIDList = [
        {name: "id_location", latName: "lat", lngName: "lng", bbName : "bb"},
        {name: "id_locationEnd", latName: "latEnd", lngName: "lngEnd", bbName : "bbEnd"}
    ]
    const inputs = getInputs(inputIDList)
    for(var i = 0; i < inputs.length; i++){
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
            // values / elements not given
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
        document.getElementById("thisForm").querySelectorAll(`[name=${i.name}]`).forEach(function(r) {
          if (r.checked) return (allAreFilled = allAreFilled && true);
        })
      }
      allAreFilled = allAreFilled && i.value;
      console.log(i, allAreFilled)
  });
  return allAreFilled;
}

function save_without_active(){
    var checkbox= document.getElementById("id_active")
    checkbox.checked = false
    var form = document.getElementById("thisForm");
    form.action = "/offers/save"
    form.submit();
}

function save_with_active(){
    var checkbox= document.getElementById("id_active")
    checkbox.checked = true
    var form = document.getElementById("thisForm");
    validate = validateForm()
    if (!validate){
        alert('Fill all the fields');
        return
    }
    form.submit();
}