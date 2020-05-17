var FAV_URL = "/fav/";


function toggle_fav(id)
{
    var request = new XMLHttpRequest();
    request.open("GET", location.origin + FAV_URL + id);
    request.send(null);

}

