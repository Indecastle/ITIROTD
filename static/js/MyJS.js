function menu_toogle() {
  var x = document.getElementById("myheader");
  if (x.className === "sub_headers") {
    x.className += " responsive";
  } else {
    x.className = "sub_headers";
  }
}