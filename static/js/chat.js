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
    websocket = new WebSocket("ws://127.0.0.1:6789/"),
    users = [];


my_form.onsubmit = function (event) {
    event.preventDefault();
    websocket.send(JSON.stringify({action: 'send_message', text: text_message.value}));
    text_message.value = '';
    return false;
}

function render_message(text, who) {
    var div = document.createElement("div");
    var div2 = document.createElement("div");
    var p = document.createElement("p");
    var br = document.createElement("br");
    var p2 = document.createElement("p");

    div.classList.add("chatbox__messages__user-message");
    div2.classList.add("chatbox__messages__user-message--ind-message");
    p.classList.add("name");
    p2.classList.add("message");
    p.innerHTML = text;
    p2.innerHTML = who;

    div2.appendChild(p);
    div2.appendChild(br);
    div2.appendChild(p2);
    div.appendChild(div2);
    chat_list.appendChild(div);
}

function render_users() {
    user_list.innerHTML = '';
    for (let nickname of users) {
        var div = document.createElement("div");
        var p = document.createElement("p");
        div.classList.add("chatbox__user--active");
        p.textContent = nickname;
        div.appendChild(p);
        user_list.appendChild(div);
    }
}

websocket.onmessage = function (event) {
    data = JSON.parse(event.data);
    console.log(data)
    switch (data.type) {
        case 'get_messages':
            for (let [text, who] of data.messages) {
                render_message(text, who)
            }
            break;
        case 'get_one_message':
            render_message(data.text, data.who)
            break;
        case 'users':
            users = data.users;
            render_users();
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
