function remove_suggestions(bookmark) {
    input = bookmark.querySelector(".prediction").innerText = ""
}


function match_tags(bookmark) {
    input = bookmark.querySelector("input[name='tags']").value
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

function predict_input (bookmark) {
    var tag_results = match_tags(bookmark);
    bookmark.querySelector(".prediction").innerHTML = tag_results.join(" ");
}
