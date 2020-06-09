function remove_suggestions(predict_paren) {
    input = predict_paren.querySelector(".prediction").innerText = ""
}


function match_tags(predict_paren) {
    input = predict_paren.querySelector("input[name='tags']").value
    var reg = new RegExp("^" + input.split(/[ ,]+/).slice(-1)[0] , 'i');
    return tag_list.filter(function(tag_prediction) {
        // if regex is empty, erase
        if(reg == "/^/i") {
            return
        }
        if (tag_prediction.match(reg)) {
            return tag_prediction;
        }
    });
}

function create_prediction_section(predict_paren) {
    if (!predict_paren.contains(predict_paren.querySelector(".prediction"))) {
        elem = document.createElement("div")
        elem.className = "prediction"
        predict_paren.insertBefore(elem, predict_paren.querySelector("input[name='tags']").nextSibling )
    }
}

function predict_input (predict_paren) {
    create_prediction_section(predict_paren)
    var tag_results = match_tags(predict_paren);
    predict_paren.querySelector(".prediction").innerHTML = tag_results.join(" ");
}

function predict_input_page () {
    paren = document.querySelector("input[name='tags']").parentNode
    create_prediction_section(paren)
    var tag_results = match_tags(paren);
    console.log(tag_results)
    paren.querySelector(".prediction").innerHTML = tag_results.join(" ");
}

function remove_suggestions_page() {
    document.querySelector("input[name='tags']").parentNode.querySelector(".prediction").innerText = ""
}
