var FAV_URL = "/fav/";
var DELETE_URL = "/delete/"

function prepare_vals(vals) {
    var ret = [];
    for (var v in vals) {
        ret.push(v + "=" + encodeURIComponent(vals[v]));
    }
    return ret.join("&")
}

function get_cookie(name) {
    var b = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return b ? b.pop() : '';
}

function toggle_fav(id) {
    var request = new XMLHttpRequest();
    var data = {
        "csrfmiddlewaretoken": get_cookie("csrftoken"),
        "id": id
    }
    request.open("POST", location.origin + FAV_URL);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    request.send(prepare_vals(data));
    request.onload = function () {
        if (request.status == 200) {
            var bookmark = document.getElementById(id);
            bookmark.classList.toggle("faved");
            var fav = bookmark.getElementsByClassName("fav")[0];
            if (fav.innerHTML == "fav") {
                fav.innerHTML = "unfav";
            } else if (fav.innerHTML == "unfav") {
                fav.innerHTML = "fav";
            }
        } else {
            alert(`${request.status}: ${request.statusText}`);
        }
    }
}

function delete_bookmark(id) {
    var bookmark = document.getElementById(id);
    var elem = document.createElement("span");
    elem.className = "toggle-menu";
    var destroy = document.createElement("a");
    destroy.href = "#";
    destroy.innerHTML = "destroy";
    destroy.className = "destroy-confirm";
    destroy.onclick = function () {
        confirm_destroy(id);
        return false;
    }
    var cancel = document.createElement("a");
    cancel.href = "#"
    cancel.innerHTML = "cancel";
    cancel.className = "cancel-confirm";
    cancel.onclick = function () {
        cancel_delete(id);
        return false;
    }
    elem.appendChild(cancel);
    elem.appendChild(document.createTextNode("   /   "));
    elem.appendChild(destroy);
    bookmark.appendChild(elem);
    bookmark.getElementsByClassName("delete")[0].style.display = "none";
}

function cancel_delete(id) {
    var div = document.getElementById(id);
    div.getElementsByClassName("toggle-menu")[0].remove();
    div.getElementsByClassName("delete")[0].style.display = "inline";
}

function confirm_destroy(id) {
    var request = new XMLHttpRequest();
    request.open("POST", location.origin + DELETE_URL);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    var data = {
        "csrfmiddlewaretoken": get_cookie("csrftoken"),
        "id": id
    }
    request.send(prepare_vals(data));
    request.onload = function () {
        if (request.status == 200) {
            document.getElementById(id).remove();
        } else {
            alert(`${request.status}: ${request.statusText}`);
        }
    }

}