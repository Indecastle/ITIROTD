function find_cookie(key) {
    let cookie = document.cookie.split(';');
    let find_el = cookie.find((item) => item.trim().startsWith(key + '='));
    if (find_el !== undefined)
        return find_el.split('=', 2)[1];
    return undefined;
}

var user_list = document.querySelector('#user_list'),
    chat_list = document.querySelector('#chat_list'),
    my_form = document.querySelector('#my_form'),
    text_message = document.querySelector('#text_message'),
    p_is_reading = document.querySelector('#form_p'),
    websocket = new WebSocket("ws://192.168.100.3:6789/"),
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
    render_message({id: null, text: text}, my_user, true, uuid);
    websocket.send(JSON.stringify({action: 'send_message', text: text, uuid: uuid}));
    websocket.send(JSON.stringify({action: 'reading_message', is_reading: is_reading}));
    text_message.value = '';
    return false;
};

function render_message(message, user, is_new_message, uuid = 'invalid') {
    let div = document.querySelector('#new_message_' + uuid);
    if (div !== null) {
        div.id = 'message_' + message.id;
        div.style = '';
    } else {
        div = document.createElement("div");
        let div2 = document.createElement("div");
        let p = document.createElement("p");
        let br = document.createElement("br");
        let p2 = document.createElement("p");

        if (is_new_message === true) {
            div2.id = 'new_message_' + uuid;
            div2.style = 'background-color: rgba(100, 100, 100, 0.2);';
        } else {
            div2.id = 'message_' + message.id;
        }

        div.classList.add("chatbox__messages__user-message");
        div2.classList.add("chatbox__messages__user-message--ind-message");
        p.classList.add("name");
        p2.classList.add("message");
        p.innerHTML = message.text;
        p2.innerHTML = user.nickname;

        div2.appendChild(p);
        div2.appendChild(br);
        div2.appendChild(p2);
        div.appendChild(div2);
        chat_list.appendChild(div);
    }

}

function render_all_users() {
    user_list.innerHTML = '';
    for (let user of all_users) {
        var div = document.createElement("div");
        var p = document.createElement("p");
        div.classList.add("chatbox__user--active");
        p.textContent = user.nickname;
        div.appendChild(p);
        user_list.appendChild(div);
        user['dom_element'] = div
    }
}

function render_users() {
    for (let user of all_users) {
        user2 = online_users.find(u => u.id === user.id);
        user.dom_element.className = '';
        // user.dom_element.classList.remove(...element.classList);
        if (user2 === undefined)
            user.dom_element.classList.add('chatbox__user--busy');
        else
            user.dom_element.classList.add('chatbox__user--active');
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

websocket.onmessage = function (event) {
    var data = JSON.parse(event.data);
    console.log(data);
    switch (data.type) {
        case 'init':
            my_user = data.user;
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
    session: find_cookie("SessionId"),
    chat_id: searchParams.get('chat_id'),
    password: searchParams.get('pass')
}));


/*
setInterval(function(){
   if(is_focus === 1) {
       showNotification("YES");
   }
   else {
        showNotification();
   }
}, 2000);
*/