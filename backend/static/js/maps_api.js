function initAutocomplete() {
    const input = document.getElementById("location");

    if (input !== null) {
        autocomplete = new google.maps.places.Autocomplete(input, {
            type:"geocode"
        });
        autocomplete.setComponentRestrictions({
            // EU-countries + EFTA-countries + UK
            country: ["be", "bg", "cz", "dk", "de", "ee", "ie", "el", "es", "fr", "hr", "it", "cy", "lv", "lt", "lu", "hu", "mt", "nl", "at", "pl", "pt", "ro", "si", "sk", "fi", "se",    "is", "no", "ch", "li", "uk"],
        });   
          
        autocomplete.addListener("place_changed", () => {
            input.focus();
        });
    }
}