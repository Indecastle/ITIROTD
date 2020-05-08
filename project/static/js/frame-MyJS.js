function menu_toogle() {
    var x = document.getElementById("myheader");
    if (x.className === "sub_headers") {
        x.className += " responsive";
    } else {
        x.className = "sub_headers";
    }
}

function toggleNav() {
    var el = document.querySelector(".chat-left-infobar");
    el.style.width = el.style.width === '0px' ? '165px' : '0px';
}

function calc_width_message(width) {
    return window.innerWidth > 750 ? (width - 165) * 0.6 : width * 0.6
}

function init_chat() {
    var el = document.getElementById("chat-box");
    if (el !== null) {
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

function init_menu_toggle() {
    var button = document.getElementById("nav-toggle_id");
    if (button !== null) {
        button.addEventListener('click', menu_toogle);
    }
}


window.addEventListener("load", () => {
    init_menu_toggle()

    if (init_create_chat_form()) {
    } else if (init_chat()) {
    }
});