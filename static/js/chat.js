function find_cookie(key) {
    let cookie = document.cookie.split(';');
    let find_el = cookie.find((item) => item.trim().startsWith(key + '='));
    if (find_el !== undefined)
        return find_el.split('=', 2)[1];
    return undefined;
}

function timeConverter(UNIX_timestamp) {
    var a = new Date(UNIX_timestamp * 1000);
    console.log(a);
    console.log(UNIX_timestamp);
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var year = a.getFullYear();
    var month = months[a.getMonth()];
    var date = a.getDate();
    var hour = a.getHours();
    var min = a.getMinutes();
    var sec = a.getSeconds();
    var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec;
    return time;
}

var user_list = document.querySelector('#user_list'),
    chat_list = document.querySelector('#chat_list'),
    parent_chat_list = chat_list.parentElement.parentElement,
    my_form = document.querySelector('#my_form'),
    chat_form_users = document.querySelector('#chat_form_users'),
    text_message = document.querySelector('#text_message'),
    p_is_reading = document.querySelector('#form_p'),
    already_messages = document.querySelector('#already_messages'),
    chat_header = document.querySelector('#chat_header'),
    websocket = new WebSocket("wss://localhost:6789/"),
    all_messages = [],
    online_users = [],
    all_users = [],
    my_user,
    invalid_user = {'id': -1, 'is_reading': null};


var is_reading = null;
my_form.form_message.oninput = () => {
    let is_reading2 = my_form.form_message.value !== '';
    if (is_reading !== is_reading2) {
        is_reading = is_reading2;
        websocket.send(JSON.stringify({action: 'reading_message', is_reading: is_reading}));
    }
};


my_form.onsubmit = function (event) {
    event.preventDefault();
    is_reading = false;
    let uuid = create_UUID();
    let text = text_message.value;
    render_message({id: null, text: text, when: Date.now() / 1000}, my_user, true, uuid);
    websocket.send(JSON.stringify({action: 'send_message', text: text, uuid: uuid}));
    websocket.send(JSON.stringify({action: 'reading_message', is_reading: is_reading}));
    text_message.value = '';
    return false;
};

function render_message(message, user, is_new_message, uuid = 'invalid') {
    let div = document.querySelector('#new_message_' + uuid);
    if (div !== null) {
        let finded_message = all_messages.find(mes => mes.id === uuid);
        Object.assign(finded_message, message);
        div.id = 'message_' + message.id;
        // div.style = '';
        div.classList.remove("chatbox_nosend");
        if (user.id === my_user.id)
            div.classList.add('chatbox_noreaded')
    } else {
        var is_bottom = parent_chat_list.scrollHeight - parent_chat_list.scrollTop === parent_chat_list.clientHeight;

        var n_li = document.createElement("li");
        var n_div1 = document.createElement("div");
        var n_span1 = document.createElement("span");
        var n_span2 = document.createElement("span");
        var n_i = document.createElement("i");
        var n_div2 = document.createElement("div");

        n_span1.classList.add("chat-message-data-time");
        n_span2.classList.add("chat-message-data-name");
        n_i.className = "fa fa-circle";
        n_div1.className = "chat-message-data";

        if (user.id === my_user.id) {
            n_li.classList.add("chat-clearfix");
            n_i.classList.add("chat-online");
            n_div2.className = "chat-message chat-my-message";
            n_div1.appendChild(n_i);
            n_div1.appendChild(n_span2);
            n_div1.appendChild(n_span1);

        } else {
            n_li.classList.add("chat-clearfix");
            n_div1.classList.add("chat-align-right");
            n_i.classList.add("chat-me");
            n_div2.className = "chat-message chat-other-message chat-float-right";
            n_div1.appendChild(n_span1);
            n_div1.appendChild(n_span2);
            n_div1.appendChild(n_i);
        }

        n_div2.innerHTML = message.text;
        n_span1.innerHTML = timeConverter(message.when);
        n_span2.innerHTML = user.nickname;


        n_li.appendChild(n_div1);
        n_li.appendChild(n_div2);
        chat_list.appendChild(n_li);

        message['dom_element'] = n_li;
        all_messages.push(message);

        if (is_new_message === true) {
            message.id = uuid;
            n_li.id = 'new_message_' + uuid;
            n_li.classList.add("chatbox_nosend");
            // div2.style = 'background-color: rgba(100, 100, 100, 0.2);';
        } else {
            n_li.id = 'message_' + message.id;
        }

        if (message.isreaded === false)
            n_li.classList.add('chatbox_noreaded')

        if (is_bottom)
            parent_chat_list.scrollTop = parent_chat_list.scrollHeight;
        already_messages.innerHTML = "already " + all_messages.length + " messages";

    }
}

function action_onfocus(user_id) {
    var filter_messages = all_messages; //.filter(mes => mes.user_id === my_user.id);
    var user = online_users.find(user => user.id === user_id);
    if (my_user.id !== user_id) {
        filter_messages.forEach(mes => mes.dom_element.classList.remove('chatbox_noreaded'));
    }

}

function render_all_users() {
    user_list.innerHTML = '';
    for (let user of all_users) {
        let li = document.createElement("li");
        let img = document.createElement("img");
        let div = document.createElement("div");
        let div2 = document.createElement("div");
        let div3 = document.createElement("div");
        let i = document.createElement("i");
        let span = document.createElement("span");

        li.classList.add("chat-clearfix");
        img.src = '/' + user.photopath;
        img.setAttribute("onerror", "this.onerror=null;this.src='/static/agent.png'");
        img.setAttribute('height', '55px');
        img.setAttribute('width', '55px');
        img.alt = 'avatar';
        div.classList.add("chat-about");
        div2.classList.add("chat-name");
        div3.classList.add("chat-status");
        i.className = "fa fa-circle chat-online";

        div3.appendChild(i);
        div3.appendChild(span);
        div.appendChild(div2);
        div.appendChild(div3);
        li.appendChild(img);
        li.appendChild(div);
        user_list.appendChild(li);
        div2.innerHTML = user.nickname;
        user['dom_element'] = li;
        user['dom_element_status'] = span;
    }
}

function render_users() {
    for (let user of all_users) {
        let user2 = online_users.find(u => u.id === user.id);
        let i = user.dom_element.querySelector('i');
        // user.dom_element.classList.remove(...element.classList);
        if (user2 === undefined) {
            i.classList.remove('chat-online');
            i.classList.add('chat-offline');
            user.dom_element_status.innerHTML = "offline";
        }
        else {
            i.classList.remove('chat-offline');
            i.classList.add('chat-online');
            user.dom_element_status.innerHTML = "online";
        }

    }
}

function action_is_reading(user, users_is_reading) {
    users_name = users_is_reading.filter(user => user.id !== my_user.id).map(user => user.nickname);
    if (users_name.length > 0) {
        p_is_reading.innerHTML = 'reading...' + JSON.stringify(users_name);
    } else {
        p_is_reading.innerHTML = '';
    }
}

function init_myuser() {
    const img = chat_header.querySelector('img');
    img.src = '/' + my_user.photopath;
    img.setAttribute("onerror", "this.onerror=null;this.src='/static/agent.png'");
    chat_header.children[1].children[0].innerHTML = my_user.nickname;
}

websocket.onmessage = function (event) {
    var data = JSON.parse(event.data);
    console.log(data);
    switch (data.type) {
        case 'init':
            if (data.is_focus) {
            }
            my_user = data.user;
            already_messages.innerHTML = "already 0 messages";
            init_myuser();
            break;
        case 'all_users':
            all_users = data.users;
            render_all_users();
            break;
        case 'get_messages':
            chat_list.innerHTML = '';
            for (let [message, user] of data.messages) {
                render_message(message, user);
            }
            break;
        case 'get_one_message':
            if (!is_focus) {
                showNotification(data.user.nickname, data.message.text, data.message.id);
            }
            render_message(data.message, data.user, false, data.uuid);
            break;
        case 'users':
            online_users = data.users;
            render_users();
            // action_is_reading(invalid_user, null);
            break;
        case 'is_reading':
            action_is_reading(data.user, data.users_is_reading);
            break;
        case 'window_onfocus':
            action_onfocus(data.user_id);
            break;
        case 'redirect':
            console.log('REDIRECT');
            window.location.href = "/";
            break;
        default:
            console.error(
                "unsupported event", data);
    }
};

var searchParams = new URLSearchParams(window.location.search);
websocket.onopen = () => websocket.send(JSON.stringify({
    action: 'init',
    sessionHash: find_cookie("SessionHash"),
    user_id: find_cookie("user_id"),
    chat_id: searchParams.get('chat_id'),
    // password: searchParams.get('pass')
}));


setInterval(function () {
    if (is_focus === 1) {
        websocket.send(JSON.stringify({action: 'window_onfocus'}));
    } else {
    }
}, 2000);


function toggleNav() {
    var el = document.getElementById("people-list");
    el.style.width = el.style.width === '0px' ? '260px' : '0px';
}

function mediawidth(x) {
    var el = document.getElementById("people-list");
    var el_button = document.getElementById('chat-nav-button');
    if (x.matches) {
        el.style.width = '0px';
        // el_button.style.display = '';
    } else {
        el.style.width = '260px';
        // el_button.style.display = 'none';
    }
}

window.onload = () => {
    var x = window.matchMedia("(max-width: 750px)")
    mediawidth(x);
    x.addListener(mediawidth); // Attach listener function on state changes
}

var shiftDown = false;
function initChatEvent() {
    var messageBox = my_form.form_message;
    var button = document.getElementById("form_button")
    document.onkeypress = function (e) {
        if (e.keyCode === 13) {
            if (document.activeElement === messageBox && !shiftDown) {
                e.preventDefault(); // prevent another \n from being entered
                button.click();
            }
        }
    };

    document.onkeydown = function (e) {
        if (e.keyCode === 16) shiftDown = true;
    };

    document.onkeyup = function (e) {
        if (e.keyCode === 16) shiftDown = false;
    };
}
initChatEvent();

chat_form_users.onsubmit = function (event) {
    event.preventDefault();
    let text = chat_form_users.text_message.value;

    all_users.forEach((user) => {
        if (user.nickname.toLowerCase().includes(text.toLowerCase()))
            user.dom_element.style.display = '';
        else
            user.dom_element.style.display = 'none';
    })
    return false;
};

chat_form_users.querySelector('i').onclick = () => {
    chat_form_users.button.click();
};
