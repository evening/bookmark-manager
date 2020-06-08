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
            fav = bookmark.querySelector(".fav");
            if (fav.innerHTML == "fav") {
                fav.innerHTML = "unfav";
            } else if (fav.innerHTML == "unfav") {
                fav.innerHTML = "fav";
            }
        } else {
            alert(`${response.status}: ${response.responseText}`);
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
    bookmark.querySelector(".delete").style.display = "none";
}

function cancel_delete(id) {
    div = document.getElementById(id);
    div.querySelector(".toggle-menu").remove();
    div.querySelector(".delete").style.display = "inline";
}

function confirm_destroy(id) {
    response = send_post_request(id, DELETE_URL)
    response.onload = function () {
        if (response.status == 200) {
            document.getElementById(id).remove();
        } else {
            alert(`${response.status}: ${response.responseText}`);
        }
    }
}

function parse_tags(bookmark) {
    if (!bookmark.contains(bookmark.querySelector(".tags"))) {
        return ""
    }

    s = bookmark.querySelector(".tags").innerText
    ret = s.split(" ")
    ret.shift();
    ret.pop();
    return ret.join(" ")
}

function edit_bookmark(id) {
    request = new XMLHttpRequest();
    data = {
        "csrfmiddlewaretoken": get_cookie("csrftoken"),
    }

    // request.open("POST", "http://127.0.0.1:8000/data/189");
    // request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    // request.send(prepare_vals(data));
    // request.responseType = "json"
    // request.onload = function() {
    //     post_data = request.response;
    // }

    bookmark = document.getElementById(id);
    c = bookmark.children
    edit_menu = document.createElement("div")
    edit_menu.className = "edit-menu";

    tags = document.createElement("input")
    tags.name = "tags"
    tags.value = parse_tags(bookmark)

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
    edit_menu.appendChild(document.createElement("br"))
    edit_menu.appendChild(url);
    edit_menu.appendChild(document.createElement("br"))
    edit_menu.appendChild(tags);

    edit_menu.appendChild(document.createElement("br"))

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
        d = get_form_data(id)
        form_data = {
            "url": d[0],
            "title": d[1],
            "tags": d[2]
        }
        update_bookmark(id, form_data);
        clear_edit_menu(id);
    }
}

function get_form_data(id) {
    url = document.getElementById(id).querySelector("input[name=url]").value
    title = document.getElementById(id).querySelector("input[name=title]").value
    tags = document.getElementById(id).querySelector("input[name=tags]").value
    return [url, title, tags]
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


function update_bookmark(id, form_data) {
    response = send_post_request(id, EDIT_URL, form_data)
    response.onload = function () {
        if (response.status == 200) {
            bookmark = document.getElementById(id);
            updated_data = JSON.parse(response.responseText);
            /* archive gets destroyed if url updated */
            if (bookmark.querySelector(".url").href !== updated_data["url"]) {
                if (bookmark.contains(bookmark.querySelector(".archive"))) {
                    bookmark.querySelector(".archive").remove()
                }
            }
            bookmark.querySelector(".title").innerText = updated_data["title"]
            bookmark.querySelector(".url").innerText = truncate(updated_data["url"])
            bookmark.querySelector(".title").href = updated_data["url"]
            bookmark.querySelector(".url").href = updated_data["url"];
            while (bookmark.querySelector(".tags").firstChild) {
                bookmark.querySelector(".tags").removeChild(bookmark.querySelector(".tags").firstChild)
            }
            bookmark.querySelector(".tags").appendChild(generate_new_tags(updated_data["tags"]))

        } else {
            alert(`${response.status}: ${response.responseText}`);
        }
    }
}

function generate_new_tags(arr) {
    tags = document.createElement("span");
    tags.appendChild(document.createTextNode("[ "));

    arr.forEach(
        element => {
            console.log(element)
            tag = document.createElement("a");
            tag.href = window.location.href.split("#")[0] + "/t:" + element;
            tag.innerText = element
            tags.appendChild(tag);
            tags.appendChild(document.createTextNode(" "));
        }
    )
    tags.appendChild(document.createTextNode(" ]"));
    return tags
}