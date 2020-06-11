var FAV_URL = location.origin + "/fav/";
var DELETE_URL = location.origin + "/delete/";
var EDIT_URL = location.origin + "/edit/";

/* helper functions */

function prepare_vals(vals) {
  // set up variables for GET requests
  let ret = [];
  for (v in vals) {
    ret.push(v + "=" + encodeURIComponent(vals[v]));
  }
  return ret.join("&");
}

function truncate(str, i) {
  // truncate
  if (str.length < i) {
    return str;
  }
  return str.slice(0, 69) + "…";
}

function send_post_request(id, URL, extra = {}) {
  // send a post request
  let request = new XMLHttpRequest();
  let data = {
    csrfmiddlewaretoken: get_cookie("csrftoken"),
    id: id,
  };
  data = Object.assign({}, data, extra);
  request.open("POST", URL);
  request.setRequestHeader(
    "Content-Type",
    "application/x-www-form-urlencoded; charset=UTF-8"
  );
  request.send(prepare_vals(data));
  return request;
}

function get_cookie(name) {
  // get cookie (csrftoken)
  let b = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return b ? b.pop() : "";
}

function list_tags_from_string(s) {
  // take a long string and return an array of strings
  return s.split(" ").filter((e) => e);
}

function parse_tags(bookmark) {
  // convert tag span into a string for an input to take
  if (!bookmark.contains(bookmark.querySelector(".tags"))) {
    return null;
  }

  s = bookmark.querySelector(".tags").innerText;
  ret = s.split(" ");
  // shift/pop to remove the tag decorations `[` and `]`
  ret.shift();
  ret.pop();
  return ret.join(" ");
}

function generate_new_tags(arr) {
  let tags = document.createElement("span");
  tags.appendChild(document.createTextNode("[ ")); //decoration
  arr.forEach((element) => {
    let tag = document.createElement("a");
    tag.href = window.location.href.split("#")[0] + "/t:" + element;
    tag.innerText = element;
    tags.appendChild(tag);
    tags.appendChild(document.createTextNode(" "));
  });
  tags.appendChild(document.createTextNode(" ]"));
  return tags;
}

/* profile page shortcuts */

function toggle_fav(id) {
  // toggle favs
  let response = send_post_request(id, FAV_URL);
  response.onload = function () {
    if (response.status == 200) {
      let bookmark = document.getElementById(id);
      bookmark.classList.toggle("faved");
      let fav = bookmark.querySelector(".fav");
      if (fav.innerHTML == "fav") {
        fav.innerHTML = "unfav";
      } else if (fav.innerHTML == "unfav") {
        fav.innerHTML = "fav";
      }
    } else {
      alert(`${response.status}: ${response.responseText}`);
    }
  };
}

function delete_bookmark(id) {
  // open menu to delete bookmark
  let bookmark = document.getElementById(id);
  menu_delete = document.createElement("span");
  menu_delete.className = "toggle-menu";
  let option_destroy = document.createElement("a");
  option_destroy.href = "#";
  option_destroy.innerHTML = "destroy";
  option_destroy.className = "destroy-confirm";
  option_destroy.onclick = function () {
    confirm_destroy(id);
    return false;
  };
  let option_cancel = document.createElement("a");
  option_cancel.href = "#";
  option_cancel.innerHTML = "cancel";
  option_cancel.className = "cancel-confirm";
  option_cancel.onclick = function () {
    bookmark.querySelector(".toggle-menu").remove();
    bookmark.querySelector(".delete").style.display = "inline";
    return false;
  };
  menu_delete.appendChild(option_cancel);
  menu_delete.appendChild(document.createTextNode("   /   "));
  menu_delete.appendChild(option_destroy);
  bookmark.appendChild(menu_delete);
  bookmark.querySelector(".delete").style.display = "none"; //hide original delete
}

function confirm_destroy(id) {
  let response = send_post_request(id, DELETE_URL);
  response.onload = function () {
    if (response.status == 200) {
      document.getElementById(id).remove();
    } else {
      alert(`${response.status}: ${response.responseText}`);
    }
  };
}

function edit_bookmark(id) {
  let request = new XMLHttpRequest();
  let bookmark = document.getElementById(id);

  let edit_menu = document.createElement("div");
  edit_menu.className = "edit-menu";

  let tag_input = document.createElement("input");
  tag_input.name = "tags";
  // need to get the ID otherwise 'variable bookmark' might be overwritten?
  tag_input.onkeyup = predict_tag;
  tag_input.onkeydown = no_tab;
  tag_input.onblur = remove_suggestions;
  tag_input.value = parse_tags(document.getElementById(id));
  let title_input = document.createElement("input");
  title_input.name = "title";
  title_input.value = bookmark.querySelector(".title").innerText;

  let url_input = document.createElement("input");
  url_input.name = "url";
  url_input.type = "url";
  url_input.value = bookmark.querySelector(".url").href;

  let submit = document.createElement("input");
  submit.value = "submit";
  submit.type = "submit";
  let cancel = document.createElement("input");
  cancel.value = "cancel";
  cancel.type = "reset";

  edit_menu.appendChild(title_input);
  edit_menu.appendChild(document.createElement("br"));
  edit_menu.appendChild(url_input);
  edit_menu.appendChild(document.createElement("br"));
  edit_menu.appendChild(tag_input);
  edit_menu.appendChild(document.createElement("br"));
  edit_menu.appendChild(submit);
  edit_menu.appendChild(cancel);

  let c = bookmark.children;
  for (i = 0; i < c.length; i++) {
    // hide bookmark information to make room for edit menu
    c[i].style.display = "none";
  }
  bookmark.appendChild(edit_menu);

  cancel.onclick = function () {
    // go back to normal
    clear_edit_menu(bookmark);
  };

  submit.onclick = function () {
    form_data = get_form_data(id);
    data = {
      url: form_data[0],
      title: form_data[1],
      tags: form_data[2],
    };
    update_bookmark(id, data);
    clear_edit_menu(bookmark);
  };
}

function get_form_data(id) {
  let url_data = document.getElementById(id).querySelector("input[name=url]")
    .value;
  let title_data = document
    .getElementById(id)
    .querySelector("input[name=title]").value;
  let tags_data = document.getElementById(id).querySelector("input[name=tags]")
    .value;
  return [url_data, title_data, tags_data];
}

function clear_edit_menu(bookmark) {
  bookmark.querySelector(".edit-menu").remove();
  let c = bookmark.children;
  for (i = 0; i < c.length; i++) {
    c[i].style.display = "inline";
  }
  return false;
}

function update_bookmark(id, form_data) {
  let response = send_post_request(id, EDIT_URL, form_data);
  response.onload = function () {
    if (response.status == 200) {
      let bookmark = document.getElementById(id);
      let new_data = JSON.parse(response.responseText);
      /* snapshot gets destroyed if url updated */
      if (bookmark.querySelector(".url").href !== new_data["url"]) {
        if (bookmark.contains(bookmark.querySelector(".snapshot"))) {
          bookmark.querySelector(".snapshot").remove();
        }
      }
      bookmark.querySelector(".title").innerText = new_data["title"];
      bookmark.querySelector(".url").innerText = truncate(new_data["url"], 70);
      bookmark.querySelector(".title").href = new_data["url"];
      bookmark.querySelector(".url").href = new_data["url"];
      if (bookmark.contains(bookmark.querySelector(".tags"))) {
        // reset tags if it exists
        bookmark.querySelector(".tags").innerHTML = "";
      } else {
        // create tags section if it doesn't exist
        let tags = document.createElement("span");
        tags.className = "tags";
        bookmark.insertBefore(tags, bookmark.querySelector(".time"));
        bookmark.insertBefore(
          document.createElement("br"),
          bookmark.querySelector(".time")
        );
      }
      // repopulate tags
      bookmark
        .querySelector(".tags")
        .appendChild(generate_new_tags(new_data["tags"]));
    } else {
      alert(`${response.status}: ${response.responseText}`);
    }
  };
}
