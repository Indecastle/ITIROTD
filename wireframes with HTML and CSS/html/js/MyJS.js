function find_cookie(key) {
    let cookie = document.cookie.split(';');
    let find_el = cookie.find((item) => item.trim().startsWith(key + '='));
    if (find_el !== undefined)
        return find_el.split('=', 2)[1];
    return undefined;
}

function getJSON(url, callback) {
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
            tag: tag + notification_test_counter,
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


function toggleNav() {
    var el = document.querySelector(".chat-left-infobar");
    el.style.width = el.style.width === '0px' ? '165px' : '0px';
}

function mediawidth(x) {
    var el = document.querySelector(".chat-left-infobar");
    var el_button = document.getElementById('chat-nav-button');
    if (x.matches) {
        el.style.width = '0px';
        // el_button.style.display = '';
    } else {
        el.style.width = '165px';
        // el_button.style.display = 'none';
    }
}

function calc_width_message(width) {
    return window.innerWidth > 750 ? (width - 165) * 0.6 : width * 0.6
}

function init_chat() {
    var el = document.getElementById("chat-box");
    if (el !== null) {
        var x = window.matchMedia("(max-width: 750px)")
        mediawidth(x);
        x.addListener(mediawidth); // Attach listener function on state changes

        var user_search_button = document.getElementById("chat-nav-button")
        user_search_button.onclick = toggleNav;

        function resize_messages() {
            var w = el.clientWidth;
            var elements = el.getElementsByClassName("chat-message-text");
            for (let el of elements) {
                el.style.maxWidth = calc_width_message(w) + 'px';
            }
        }
        resize_messages();
        window.addEventListener("resize", resize_messages);

        return true;
    }
    return false;
}

function init_create_chat_form() {
    var tag_form = document.getElementById("createchat_form");
    if (tag_form !== null) {
        var tag_select = document.getElementById("createchat_select");
        var tag_password = document.getElementById("createchat_password");

        tag_select.onchange = () => {
            tag_password.style = tag_select.value === "PUBLIC" ? "display: none;" : '';
        };
        return true;
    }
    return false;
}


function init_listchats() {
    var search_form_listchats = document.querySelector('#search_form_listchats')
    if (search_form_listchats === null)
        return false;
    var checkbox_other = search_form_listchats.checkbox_other;
    var table_body = document.querySelector('#table_body')
    checkbox_other.addEventListener('change', (event) => search_form_listchats.onsubmit(event));

    function tourl(td) {
        window.location.href = "/chat/chat?chat_id=" + td.parentElement.children[0].innerHTML;
    }

    search_form_listchats.onsubmit = function (event) {
        event.preventDefault();
        let text = search_form_listchats.text_message.value;
        let url = `/json/get_chats?search=${text}&isnotmy=${checkbox_other.checked}&count=${100}`
        getJSON(url, (out) => {
            console.log(out);
            // var tbody = document.createElement("tbody");
            table_body.innerHTML = '';
            for (let obj of out.chats) {
                let tr = document.createElement("tr");
                let td1 = document.createElement("td");
                let td2 = document.createElement("td");
                let td3 = document.createElement("td");

                td1.innerText = obj.id;
                td2.innerText = obj.name;
                td2.onclick = () => {
                    tourl(td2)
                };
                td3.innerText = obj.type;
                if (obj.type === 'PUBLIC')
                    td3.className = 'td-public';
                else
                    td3.className = 'td-private';

                tr.appendChild(td1);
                tr.appendChild(td2);
                tr.appendChild(td3);
                table_body.appendChild(tr);
            }
        })
        return false;
    };

    search_form_listchats.querySelector('i').onclick = () => {
        search_form_listchats.button.click();
    };

    // search_form_listchats.onsubmit(new CustomEvent('submit', {canselable: true} ));
    search_form_listchats.dispatchEvent(new CustomEvent('submit', {canselable: true} ));

    return true;
}


function init_menu_toggle() {
    var button = document.getElementById("nav-toggle_id");
    if (button !== null) {
        button.addEventListener('click', menu_toogle);
    }
}

window.addEventListener("load", () => {
    initNotifications();
    init_menu_toggle()

    if (init_create_chat_form()) {}
    else if (init_chat()) {}
    else if (init_listchats()) {}
    else if (init_chat()) {}
});