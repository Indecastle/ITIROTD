function menu_toogle() {
  var x = document.getElementById("myheader");
  if (x.className === "sub_headers") {
    x.className += " responsive";
  } else {
    x.className = "sub_headers";
  }
}


function animate({duration, draw, timing}) {

  let start = performance.now();

  requestAnimationFrame(function animate(time) {
    let timeFraction = (time - start) / duration;
    if (timeFraction > 1) timeFraction = 1;

    let progress = timing(timeFraction)

    draw(progress);

    if (timeFraction < 1) {
      requestAnimationFrame(animate);
    }

  });
}