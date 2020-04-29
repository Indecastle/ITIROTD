function find_cookie(key) {
    let cookie = document.cookie.split(';');
    let find_el = cookie.find((item) => item.trim().startsWith(key + '='));
    if (find_el !== undefined)
        return find_el.split('=', 2)[1];
    return undefined;
}

var getJSON = function (url, callback) {
    fetch(url, {credentials: 'include'})
        .then(res => res.json())
        .then(callback)
        .catch(err => {
            throw err
        });
}

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

function create_UUID() {
    var dt = new Date().getTime();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (dt + Math.random() * 16) % 16 | 0;
        dt = Math.floor(dt / 16);
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}

function my_sleep(ms) {
    ms += new Date().getTime();
    while (new Date() < ms) {
    }
}

var notificationsEnabled = false;

function initNotifications() {
    if (window.Notification) {
        Notification.requestPermission(function (permission) {
            if (permission === 'granted') {
                notificationsEnabled = true;
            } else {
                // alert("You denied Notifications, it's so sad :(");
            }
        });
    } else {
        // alert("Your browser doesn't support Notifications API");
    }
}
var notification_test_counter = 0
function showNotification(title, message, tag = 'tag') {
    if (notificationsEnabled) {
        notification_test_counter++;
        var notification = new Notification(title, {
            body: message,
            // icon: "/static/other/jason-leung-HM6TMmevbZQ-unsplash.jpg",
            vibrate: [200, 100, 200],
            tag: tag+notification_test_counter,
            // image: "/static/other/jason-leung-HM6TMmevbZQ-unsplash.jpg",
            badge: "/static/sun.ico",
            // actions: [{action: "Detail", title: "View", icon: "https://via.placeholder.com/128/ff0000"}]
        });

        setTimeout(function () {
            notification.close();
        }, 5000);
    } else {
        // alert("Notifications are disabled");
    }
}

var is_focus = 1;
window.onfocus = function () {
    is_focus = 1;
};
window.onblur = function () {
    is_focus = 0;
};