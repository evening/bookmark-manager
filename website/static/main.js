var FAV_URL = "/fav/";
var DELETE_URL = "/delete/"

function toggle_fav(id)
{
    var bookmark = document.getElementById(id);
    bookmark.classList.toggle("faved");
    var fav = bookmark.getElementsByClassName("fav")[0];
    if(fav.innerHTML == "fav") {
        fav.innerHTML = "unfav";
    }
    else if(fav.innerHTML == "unfav") {
        fav.innerHTML = "fav";
    }
    var request = new XMLHttpRequest();
    request.open("GET", location.origin + FAV_URL + id);
    request.send(null);
}

function delete_bookmark(id) {
    var bookmark = document.getElementById(id);
    var elem = document.createElement("span");
    elem.className = "toggle-menu";
    var destroy = document.createElement("a");
    destroy.href = "#";
    destroy.innerHTML = "destroy";
    destroy.className = "destroy-confirm";
    destroy.onclick = function() {
        confirm_destroy(id); return false;
    }
    var cancel = document.createElement("a");
    cancel.href = "#"
    cancel.innerHTML = "cancel";
    cancel.className = "cancel-confirm";
    cancel.onclick = function() {
        cancel_delete(id); return false;
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
    request.open("GET", location.origin + DELETE_URL + id);
    request.send(null);
    document.getElementById(id).remove();
}