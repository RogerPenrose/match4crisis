function initMapsAutocomplete(){
    let input = document.getElementById("location");
    if (input == null || input.nodeName !== "INPUT"){
        input = document.getElementById("id_location")
    }
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
                const bb = document.getElementsByName("bb")[0];
                const place = autocomplete.getPlace();
                lat.value = place.geometry.location.lat();
                lng.value = place.geometry.location.lng();
                if (place.geometry.viewport){
                    bb.value = JSON.stringify(place.geometry.viewport)
                }
            } catch {
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

            document.getElementsByName("lat")[0].setAttribute("value", urlParams.get('lat'));
            document.getElementsByName("lng")[0].setAttribute("value", urlParams.get('lng'));
            document.getElementsByName("bb")[0].setAttribute("value", urlParams.get('bb'));
        } catch {
            // either we on mapview_page or just not given
        }

        return autocomplete;
    }
}

function init_google_maps() {
    if (typeof initMap === "function") initMap() // we are at mapview
    else if (typeof mapViewPage === "object") mapViewPage.initAutocomplete() // we are at /offers
    else if (typeof offer_autocomplete === "object") offer_autocomplete() // we are at /offers/createOffer
    else initMapsAutocomplete();
}