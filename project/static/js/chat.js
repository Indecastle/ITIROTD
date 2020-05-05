function img_error(event) {
    event.target.onerror = null;
    event.target.src = '/static/agent.png'

}

function timeConverter(UNIX_timestamp) {
    var a = new Date(UNIX_timestamp * 1000);
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
    parent_chat_list = chat_list, //document.querySelector('#chat_list'),
    my_form = document.forms.my_form, //document.querySelector('#my_form'),
    chat_form_users = document.querySelector('#chat_form_users'),
    text_message = document.querySelector('#text_message'),
    chat_nav_button = document.querySelector('#chat-nav-button'),
    span_is_reading = document.querySelector('#form_isreading'),
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
    if (text.trim() !== '') {
        render_message({id: null, text: text, when: Date.now() / 1000}, my_user, true, uuid);
        websocket.send(JSON.stringify({action: 'send_message', text: text, uuid: uuid}));
        websocket.send(JSON.stringify({action: 'reading_message', is_reading: is_reading}));
        text_message.value = '';
    }
    return false;
};

function render_message(message, user, is_new_message, uuid = 'invalid') {
    let div1 = document.querySelector('#new_message_' + uuid);
    if (div1 !== null) {
        let finded_message = all_messages.find(mes => mes.id === uuid);
        let status = finded_message.dom_element_status;
        Object.assign(finded_message, message);
        div1.id = 'message_' + message.id;
        // div.style = '';
        status.classList.remove("chat_message_nosend");
        if (user.id === my_user.id)
            status.classList.add('chat_message_noreaded')
    } else {
        var is_bottom = parent_chat_list.scrollHeight - parent_chat_list.scrollTop === parent_chat_list.clientHeight;

        var n_div1 = document.createElement("div");
        var n_img = document.createElement("img");
        var n_div2 = document.createElement("div");
        var n_strong = document.createElement("strong");
        var n_span = document.createElement("span");
        var n_div3 = document.createElement("div");

        n_div1.classList.add("chat-message-box");
        // n_img.setAttribute("onerror", "this.onerror=null;this.src='/static/agent.png'");
        n_img.onerror = img_error;
        n_div2.classList.add("chat-message-main-box");
        n_div3.className = "chat-message-text";

        n_img.src = '/' + user.photopath;
        n_strong.innerText = user.nickname;
        n_span.innerText = timeConverter(message.when);
        n_div3.innerText = message.text;

        n_div2.appendChild(n_strong);
        n_div2.appendChild(n_span);
        n_div2.appendChild(n_div3);
        n_div1.appendChild(n_img);
        n_div1.appendChild(n_div2);

        chat_list.appendChild(n_div1);

        message['dom_element'] = n_div1;
        message['dom_element_status'] = n_div3;
        all_messages.push(message);

        if (is_new_message === true) {
            message.id = uuid;
            n_div1.id = 'new_message_' + uuid;
            n_div3.classList.add("chat_message_nosend");
            // div2.style = 'background-color: rgba(100, 100, 100, 0.2);';
        } else {
            n_div1.id = 'message_' + message.id;
        }

        if (message.isreaded === false)
            n_div1.classList.add('chat_message_noreaded')

        if (is_bottom)
            parent_chat_list.scrollTop = parent_chat_list.scrollHeight;
        already_messages.innerHTML = "already " + all_messages.length + " messages";

    }
}

function action_onfocus(user_id) {
    var filter_messages = all_messages; //.filter(mes => mes.user_id === my_user.id);
    var user = online_users.find(user => user.id === user_id);
    if (my_user.id !== user_id) {
        filter_messages.forEach(mes => mes.dom_element_status.classList.remove('chat_message_noreaded'));
    }
}

function render_all_users() {
    user_list.innerHTML = '';
    for (let user of all_users) {
        let li = document.createElement("li");
        let img = document.createElement("img");
        let i = document.createElement("i");
        let span = document.createElement("span");

        img.src = '/' + user.photopath;
        img.onerror = img_error;
        img.setAttribute('height', '55px');
        img.setAttribute('width', '55px');
        img.alt = 'avatar';
        i.className = "fa fa-circle chat-online";
        span.textContent = user.nickname;

        li.appendChild(img);
        li.appendChild(i);
        li.appendChild(span);
        user_list.appendChild(li);

        user['dom_element'] = li;
        user['dom_element_status'] = i;
    }
}

function render_users() {
    for (let user of all_users) {
        let user2 = online_users.find(u => u.id === user.id);
        let i = user.dom_element_status;
        // user.dom_element.classList.remove(...element.classList);
        if (user2 === undefined) {
            i.classList.remove('chat-online');
            i.classList.add('chat-offline');
        } else {
            i.classList.remove('chat-offline');
            i.classList.add('chat-online');
        }
    }
}

function action_is_reading(user, users_is_reading) {
    users_name = users_is_reading.filter(user => user.id !== my_user.id).map(user => user.nickname);
    if (users_name.length > 0) {
        span_is_reading.innerHTML = 'reading...' + JSON.stringify(users_name);
    } else {
        span_is_reading.innerHTML = '';
    }
}

function init_myuser() {
    const img = chat_header.children[0];
    img.src = '/' + my_user.photopath;
    img.onerror = img_error;
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