function find_cookie(key) {
    let cookie = document.cookie.split(';');
    let find_el = cookie.find((item) => item.trim().startsWith(key + '='));
    if (find_el !== undefined)
        return find_el.split('=', 2)[1];
    return undefined;
}



function getJSON(url, callback, headers={}) {
    fetch(url, {credentials: 'include', headers:headers})
        .then(res => {return res.json();})
        .then(callback)
        .catch(err => {
            throw err;
        });
}

function removeItemOnce(arr, value) {
    var index = arr.indexOf(value);
    if (index > -1) {
        arr.splice(index, 1);
    }
    return arr;
}

function menu_toogle() {
    const x = document.getElementById("myheader");
    if (x.className === "sub_headers") {
        x.className += " responsive";
    } else {
        x.className = "sub_headers";
    }
}


// function animate({duration, draw, timing}) {
//
//     let start = performance.now();
//
//     requestAnimationFrame(function animate(time) {
//         let timeFraction = (time - start) / duration;
//         if (timeFraction > 1) timeFraction = 1;
//
//         let progress = timing(timeFraction)
//
//         draw(progress);
//
//         if (timeFraction < 1) {
//             requestAnimationFrame(animate);
//         }
//
//     });
// }

function create_UUID() {
    let dt = new Date().getTime();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (dt + Math.random() * 16) % 16 | 0;
        dt = Math.floor(dt / 16);
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}

// function my_sleep(ms) {
//     ms += new Date().getTime();
//     while (new Date() < ms) {
//     }
// }

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

let notification_test_counter = 0;

function showNotification(title, message, tag = 'tag') {
    if (notificationsEnabled) {
        notification_test_counter++;
        const notification = new Notification(title, {
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
        var x = window.matchMedia("(max-width: 750px)");
        mediawidth(x);
        x.addListener(mediawidth); // Attach listener function on state changes

        var user_search_button = document.getElementById("chat-nav-button");
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

        app.websocket_chat = init_chat_2();

        return true;
    }
    return false;
}

function init_create_chat_form() {
    var tag_form = document.getElementById("createchat_form");
    if (tag_form !== null) {
        var tag_select = document.getElementById("createchat_select");
        var tag_password = document.getElementById("createchat_password");

        tag_select.onchange = (e) => {
            tag_password.style = tag_select.value === "PUBLIC" ? "display: none;" : '';
        };

        tag_form.onsubmit = async function (event) {
            event.preventDefault();
            console.log(event);
            response = await fetch(tag_form.action, {
                method: 'POST',
                body: new FormData(tag_form),
                redirect: 'follow',
            });
            console.log(response);
            console.log(Array.from(response.headers.entries()));
            if (response.redirected)
                app._follow(response.url);
            else {
                let json_data = await response.json();
                if ('message' in json_data) {
                    const message_el = tag_form.querySelector("#message_box");
                    message_el.innerHTML = json_data.message;
                }
            }
        };

        return true;
    }
    return false;
}


function init_listchats() {
    const search_form_listchats = document.querySelector('#search_form_listchats');
    if (search_form_listchats === null)
        return false;
    var checkbox_other = search_form_listchats.checkbox_other;
    var table_body = document.querySelector('#table_body')
    checkbox_other.addEventListener('change', (event) => search_form_listchats.onsubmit(event));

    search_form_listchats.onsubmit = function (event) {
        event.preventDefault();
        let text = search_form_listchats.text_message.value;
        let url = `/json/get_chats?search=${text}&isnotmy=${checkbox_other.checked}&count=${100}`
        getJSON(url, (out) => {
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
                    app._follow("/chat/chat?chat_id=" + td2.parentElement.children[0].innerHTML);
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
        });
        return false;
    };

    search_form_listchats.querySelector('i').onclick = () => {
        search_form_listchats.button.click();
    };

    // search_form_listchats.onsubmit(new CustomEvent('submit', {cancelable: true} ));
    search_form_listchats.dispatchEvent(new CustomEvent('submit', {cancelable: true} ));

    return true;
}


function init_menu_toggle() {
    var button = document.getElementById("nav-toggle_id");
    if (button !== null) {
        button.addEventListener('click', menu_toogle);
    }
}


function init_auth_login() {
    var form_login = document.getElementById("login_form");
    if (form_login === null) {
        return false;
    }

    form_login.onsubmit = async function (event) {
        event.preventDefault();
        response = await fetch(form_login.action, {
            method: 'POST',
            body: new FormData(form_login)
        });
        let json_data = await response.json();
        if ('redirect' in json_data) {
            app._render_header_right(json_data.header_right);
            app._follow(json_data.newurl);
        }
        else {
            if ('message' in json_data) {
                const message_el = form_login.querySelector("#message_box");
                message_el.innerHTML = json_data.message;
            }
        }
    };

    return true;
}


function init_auth_register() {
    var form_register = document.getElementById("register_form");
    if (form_register === null) {
        return false;
    }

    form_register.onsubmit = async function (event) {
        event.preventDefault();
        response = await fetch(form_register.action, {
            method: 'POST',
            body: new FormData(form_register)
        });
        let json_data = await response.json();
        if ('redirect' in json_data) {
            app._render_header_right(json_data.header_right);
            app._follow(json_data.newurl);
        }
        else {
            if ('message' in json_data) {
                const message_el = form_register.querySelector("#message_box");
                message_el.innerHTML = json_data.message;
            }
        }
    };

    return true;
}

function init_enjoy_chat() {
    var form_enjoy = document.getElementById("enjoy_form");
    if (form_enjoy === null) {
        return false;
    }

    form_enjoy.onsubmit = async function (event) {
        event.preventDefault();
        response = await fetch(form_enjoy.action, {
            method: 'POST',
            body: new FormData(form_enjoy)
        });
        let json_data = await response.json();
        if ('redirect' in json_data) {
            app._follow(json_data.newurl);
        }
        else {
            if ('message' in json_data) {
                const message_el = form_enjoy.querySelector("#message_box");
                message_el.innerHTML = json_data.message;
            }
        }
    };

    return true;
}





var app = {

    ui: {},
    config: { mainPage: '/' },
    websocket_chat: null,


    _bindHandlers() {
        app._bindlinks();
        window.onpopstate = app._popState;
    },

    _bindlinks() {
        const links = document.body.querySelectorAll('[data-link="ajax"]');
        for (let link of links)
            link.onclick = app._navigate;
    },

    init() {
        this.ui.title = document.getElementById("title");
        this.ui.main = document.getElementById("main_dynamic");
        this.ui.header_right = document.getElementById("nav_header_right");
        this.config.siteTitle = this.ui.title.dataset.title;


        var page = document.location.pathname + document.location.search;
        this._loadPage(page);

       this._bindHandlers();
    },


    // Клик по ссылке
    _navigate(e) {
        e.stopPropagation();
        e.preventDefault();

        var page = e.target.href;
        app._follow(page);
    },

    _reload_websocket() {
        if (app.websocket_chat !== null){
            app.websocket_chat.close();
            app.websocket_chat = null;
        }
    },

    _follow(page) {
        app._loadPage(page);
        history.pushState({page: page}, '', page);
    },

    _render_header_right(html) {
        app.ui.header_right.innerHTML = html;
        console.log(app.ui.header_right);
        console.warn(html);
    },

    _popState(e) {
        const page = (e.state && e.state.page) || app.config.mainPage;
        app._loadPage(page);
    },

    // Загрузка контента по странице
    _loadPage(page) {
        getJSON(page, function(json_data) {
            document.title = json_data.title + ' | ' + app.config.siteTitle;
            app.ui.main.innerHTML = json_data.html;

            app._reload_websocket();
            app._bindlinks();
            if (init_create_chat_form()) {}
            else if (init_chat()) {}
            else if (init_listchats()) {}
            else if (init_auth_login()) {}
            else if (init_auth_register()) {}
            else if (init_enjoy_chat()) {}
        },
            headers={'ajax': true});


    }
};

window.addEventListener("load", () => {
    initNotifications();
    init_menu_toggle();

    const main = document.getElementById("main_dynamic");
    if (main !== null)
        app.init();
});

// document.addEventListener("DOMContentLoaded", function(event) {
//   //do work
// });