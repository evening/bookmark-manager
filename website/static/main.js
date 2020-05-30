var FAV_URL = location.origin + "/fav/";
var DELETE_URL = location.origin + "/delete/"
var EDIT_URL = location.origin + "/edit/"

function prepare_vals(vals) {
    ret = [];
    for (v in vals) {
        ret.push(v + "=" + encodeURIComponent(vals[v]));
    }
    return ret.join("&")
}

function truncate(str) {
    if (str.length <= 69) {
        return str
    }
    return str.slice(0, 69) + "…"
}


function send_post_request(id, URL, extra = {}) {
    request = new XMLHttpRequest();
    data = {
        "csrfmiddlewaretoken": get_cookie("csrftoken"),
        "id": id
    }
    data = Object.assign({}, data, extra)
    request.open("POST", URL);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    request.send(prepare_vals(data));
    return request;
}

function get_cookie(name) {
    b = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return b ? b.pop() : '';
}

function toggle_fav(id) {
    response = send_post_request(id, FAV_URL)
    response.onload = function () {
        if (response.readyState == 4 && response.status == 200) {
            bookmark = document.getElementById(id);
            bookmark.classList.toggle("faved");
            fav = bookmark.getElementsByClassName("fav")[0];
            if (fav.innerHTML == "fav") {
                fav.innerHTML = "unfav";
            } else if (fav.innerHTML == "unfav") {
                fav.innerHTML = "fav";
            }
        } else {
            alert(`${response.status}: Error toggling favorite.`);
        }
    }
}

function delete_bookmark(id) {
    bookmark = document.getElementById(id);
    elem = document.createElement("span");
    elem.className = "toggle-menu";
    destroy = document.createElement("a");
    destroy.href = "#";
    destroy.innerHTML = "destroy";
    destroy.className = "destroy-confirm";
    destroy.onclick = function () {
        confirm_destroy(id);
        return false;
    }
    cancel = document.createElement("a");
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
    div = document.getElementById(id);
    div.getElementsByClassName("toggle-menu")[0].remove();
    div.getElementsByClassName("delete")[0].style.display = "inline";
}

function confirm_destroy(id) {
    response = send_post_request(id, DELETE_URL)
    response.onload = function () {
        if (response.status == 200) {
            document.getElementById(id).remove();
        } else {
            alert(`${response.status}: Error destroying`);
        }
    }
}

function edit_bookmark(id) {
    bookmark = document.getElementById(id)
    c = bookmark.children
    edit_menu = document.createElement("div")
    edit_menu.className = "edit-menu";
    // edit_menu = document.createElement("form")
    // edit_menu.method = "post"
    // edit_menu.action = "/edit/"

    // csrf = document.createElement("input")
    // csrf.name = "csrfmiddlewaretoken"
    // csrf.value = get_cookie("csrftoken")
    // csrf.type = "hidden"
    // id_hidden = document.createElement("input")
    // id_hidden.name = "id"
    // id_hidden.value = id
    // id_hidden.type = "hidden"

    br = document.createElement("br");
    title = document.createElement("input")
    title.name = "title"
    title.value = bookmark.querySelector(".title").innerText

    url = document.createElement("input")
    url.name = "url"
    url.type = "url"
    url.value = bookmark.querySelector(".url").href

    submit = document.createElement("input")
    submit.value = "submit";
    submit.type = "submit"
    cancel = document.createElement("input")
    cancel.value = "cancel";
    cancel.type = "reset";
    // edit_menu.appendChild(csrf);
    // edit_menu.appendChild(id_hidden);
    edit_menu.appendChild(title);
    edit_menu.appendChild(br)
    edit_menu.appendChild(url);
    edit_menu.appendChild(submit);
    edit_menu.appendChild(cancel);

    for (i = 0; i < c.length; i++) {
        c[i].style.display = "none";
    }
    bookmark.appendChild(edit_menu);

    cancel.onclick = function () {
        clear_edit_menu(id);
    }

    submit.onclick = function () {
        form_data = {
            "url": url.value,
            "title": title.value,
        }
        update_bookmark(id, form_data);
        clear_edit_menu(id);

    }
}

function clear_edit_menu(id) {
    bookmark = document.getElementById(id)
    edit_menu = bookmark.querySelector(".edit-menu")
    edit_menu.remove()
    c = bookmark.children

    for (i = 0; i < c.length; i++) {
        c[i].style.display = "inline";
    }
    return false;
}


function update_bookmark(id) {
    response = send_post_request(id, EDIT_URL, form_data)
    response.onload = function () {
        if (response.status == 200) {
            bookmark = document.getElementById(id);
            updated_data = JSON.parse(response.responseText);
            bookmark.querySelector(".title").innerText = updated_data["title"]
            bookmark.querySelector(".url").innerText = truncate(updated_data["url"])
            bookmark.querySelector(".title").href = updated_data["url"]
            bookmark.querySelector(".url").href = updated_data["url"]
        } else {
            alert(`${response.status}: Error updating`);
        }
    }

}