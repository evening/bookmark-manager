function remove_suggestions() {
    event.target.parentNode.querySelector(".prediction").innerText = ""
}

function autocomplete_remove_last_word(s) {
    if(s.split(" ").length > 1) {
        // add a space before the new word, if there's a word before it
        return s.substring(0, s.lastIndexOf(" ")) + " ";
    }
    return s.substring(0, s.lastIndexOf(" "));
}

function no_tab() {
    if (event.keyCode == 9) {
        event.preventDefault(); 
    }
}

function match_tags(elem) {
    let value = elem.value
    var reg = new RegExp("^" + value.split(/[ ,]+/).slice(-1)[0] , 'i');
    return tag_list.filter(function(tag_prediction) {
        // if regex is empty, erase
        if(reg == "/^/i") {
            return null
        }
        if (tag_prediction.match(reg)) {
            return tag_prediction;
        }
    });
}

function create_prediction_section(elem) {
    // create a predictions section
    if (!elem.contains(elem.querySelector(".prediction"))) {
        let prediction = document.createElement("span")
        prediction.className = "prediction"
        elem.insertBefore(prediction, elem.querySelector("input[name='tags']").nextSibling )
    }
}

function predict_tag() {
    let elem = event.target;
    create_prediction_section(elem.parentNode);
    let tag_results = match_tags(elem);
    if (event.keyCode == 9) {
        if(tag_results.length == 0) {
            // if no prediction, just add a space. 
            if(!elem.value.endsWith(" ")) {
                elem.value += " ";
            }
        }
        if(tag_results[0]) {
            // if prediction, tab will add first prediction to input
            elem.value = autocomplete_remove_last_word(elem.value) + tag_results[0] + " ";    
            tag_results = null; // reset predictions
        }
    }
    elem.parentNode.querySelector(".prediction").innerHTML = tag_results;
}