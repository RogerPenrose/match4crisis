function initMapsAutocomplete(){
    const input = document.getElementById("location");

    if (input !== null) {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);

        const loc = urlParams.get('location')
        if (loc) {
            input.setAttribute("value", loc)
        }

        const autocomplete = new google.maps.places.Autocomplete(input, {
            type:"geocode"
        });
        autocomplete.setComponentRestrictions({
            // EU-countries + EFTA-countries + UK
            country: ["be", "bg", "cz", "dk", "de", "ee", "ie", "el", "es", "fr", "hr", "it", "cy", "lv", "lt", "lu", "hu", "mt", "nl", "at", "pl", "pt", "ro", "si", "sk", "fi", "se",    "is", "no", "ch", "li", "uk"],
        });   
          
        autocomplete.addListener("place_changed", () => {
            try {
                const lat = document.getElementsByName("lat")[0];
                const lng = document.getElementsByName("lng")[0];
                const place = autocomplete.getPlace();
                lat.value = place.geometry.location.lat();
                lng.value = place.geometry.location.lng();
            } catch {
                // either we on mapview_page or place not found or no geometry
            }
            input.focus();
        });

        return autocomplete;
    }
}

function init_google_maps() {
    if (typeof initMap === "function") initMap() // we are at mapview
    else initMapsAutocomplete();
}