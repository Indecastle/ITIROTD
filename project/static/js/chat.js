function init_chat_2() {
    function img_error(event) {
        event.target.onerror = null;
        event.target.src = '/static/agent.png'

    }

    function timeConverter(UNIX_timestamp, is_datetime = false) {
        const date = new Date(UNIX_timestamp * 1000);
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const year = date.getFullYear();
        const month = months[date.getMonth()];
        const day = date.getDate();
        const hour = date.getHours();
        const min = date.getMinutes();
        const sec = date.getSeconds();
        if (is_datetime)
            return `${year}-${date.getMonth()}-${day} ${hour}:${min}:${sec}`;
        else
            return `${day} ${month} ${year} ${hour}:${min}:${sec}`;
    }

    let chat_box = document.getElementById("chat-box"),
        user_list = document.querySelector('#user_list'),
        chat_list = document.querySelector('#chat_list'),
        parent_chat_list = chat_list, //document.querySelector('#chat_list'),
        my_form = document.forms.my_form, //document.querySelector('#my_form'),
        chat_form_users = document.querySelector('#chat_form_users'),
        text_message = document.querySelector('#text_message'),
        chat_nav_button = document.querySelector('#chat-nav-button'),
        chat_stickers = document.querySelector('#chat_stickers_list'),
        chat_sticker_button = document.querySelector('#form_button_sticker'),
        chat_select_edit_button = document.querySelector('#chat_selected_edit_message'),
        chat_select_delete_button = document.querySelector('#chat_selected_delete_message'),
        chat_stop_edit_button = document.querySelector('#chat_stop_edit_button'),
        span_is_reading = document.querySelector('#form_isreading'),
        already_messages = document.querySelector('#already_messages'),
        chat_header = document.querySelector('#chat_header'),
        websocket = new WebSocket("ws://localhost:6789/"),
        all_messages = [],
        data_stickers = [],
        online_users = [],
        all_users = [],
        my_user,
        selected_messages = [],
        selected_edit_message = null;


    let is_reading = null;
    my_form.form_message.oninput = () => {
        let is_reading2 = my_form.form_message.value !== '';
        if (is_reading !== is_reading2) {
            is_reading = is_reading2;
            websocket.send(JSON.stringify({action: 'reading_message', is_reading: is_reading}));
        }
    };

    function render_count_messages() {
        already_messages.innerHTML = all_messages.length + " messages";
    }

    function render_message(message, user, is_new_message = false, uuid = 'invalid') {
        let div1 = document.querySelector('#new_message_' + uuid);
        if (div1 !== null) {
            let finded_message = all_messages.find(mes => mes.id === uuid);
            let mess_dom = finded_message.dom_element;
            Object.assign(finded_message, message);
            div1.id = 'message_' + message.id;
            div1.dataset.id = message.id;
            // div.style = '';
            mess_dom.classList.remove("chat_message_nosend");
            if (user.id === my_user.id)
                mess_dom.classList.add('chat_message_noreaded')
        } else {
            let is_bottom = parent_chat_list.scrollHeight - parent_chat_list.scrollTop === parent_chat_list.clientHeight;

            let n_div1 = document.createElement("div");
            let n_img = document.createElement("img");
            let n_div2 = document.createElement("div");
            let n_div3 = document.createElement("div");
            let n_strong = document.createElement("strong");
            let n_time = document.createElement("time");
            let n_div4 = document.createElement("div");
            let n_img2 = document.createElement("img");

            n_div1.classList.add("chat-message-box");
            if(user.id === my_user.id)
                n_div1.classList.add("chat-message-me");
            // n_img.setAttribute("onerror", "this.onerror=null;this.src='/static/agent.png'");
            n_img.onerror = img_error;
            n_div2.classList.add("chat-message-main-box");
            n_div3.classList.add("chat-message-info-box");
            n_div4.className = "chat-message-text";
            n_div4.style.maxWidth = calc_width_message(chat_box.clientWidth) + 'px';

            n_img.src = '/' + user.photopath;
            n_strong.innerText = user.nickname;
            n_time.innerText = timeConverter(message.when);
            n_time.dateTime = timeConverter(message.when, true);


            if(message.is_sticker === true) {
                n_div4.className = "chat-message-sticker";
                n_img2.src = message.text;
                n_div4.appendChild(n_img2);
                n_div1.dataset.is_sticker = '';
            }
            else {
                n_div4.className = "chat-message-text";
                n_div4.innerText = message.text;
            }

            n_div3.appendChild(n_strong);
            n_div3.appendChild(n_time);
            n_div2.appendChild(n_div3);
            n_div2.appendChild(n_div4);
            n_div1.appendChild(n_img);
            n_div1.appendChild(n_div2);

            chat_list.appendChild(n_div1);

            message['dom_element'] = n_div1;
            message['dom_element_status'] = n_div4;
            all_messages.push(message);

            if (is_new_message === true) {
                message.id = uuid;
                n_div1.id = 'new_message_' + uuid;
                n_div1.classList.add("chat_message_nosend");
                // div2.style = 'background-color: rgba(100, 100, 100, 0.2);';
            } else {
                n_div1.id = 'message_' + message.id;
                n_div1.dataset.id = message.id;
            }

            if (user.id === my_user.id && message.isreaded === false)
                n_div1.classList.add('chat_message_noreaded');

            if (user.id === my_user.id) {
                n_div1.onclick = function(event) {
                    const new_selected_el = n_div1;
                    let message_obj = selected_messages.find(mes => mes.dom_element === new_selected_el);
                    if (message_obj === undefined) {
                        message_obj = all_messages.find(mes => mes.dom_element === new_selected_el);
                        selected_messages.push(message_obj);
                        new_selected_el.classList.add("chat_message_select");
                    }
                    else {
                        removeItemOnce(selected_messages, message_obj);
                        new_selected_el.classList.remove("chat_message_select");
                    }

                    set_classes_in_header_buttons();

                    console.log(selected_messages);
                }
            }

            if (is_bottom || is_new_message)
                parent_chat_list.scrollTop = parent_chat_list.scrollHeight;
            render_count_messages();
        }
    }

    function set_classes_in_header_buttons() {
        chat_header.classList.remove("select_show_buttons", "select_show_buttons_only_del");
        if (selected_messages.length === 1) {
            if ("is_sticker" in (selected_messages[0].dom_element.dataset))
                chat_header.classList.add("select_show_buttons_only_del");
            else
                chat_header.classList.add("select_show_buttons");
        }
        else if(selected_messages.length > 1) {
            chat_header.classList.add("select_show_buttons_only_del");
        }
    }

    function action_onfocus(user_id) {
        let filter_messages = all_messages; //.filter(mes => mes.user_id === my_user.id);
        let user = online_users.find(user => user.id === user_id);
        if (my_user.id !== user_id) {
            filter_messages.forEach(mes => mes.dom_element.classList.remove('chat_message_noreaded'));
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

    function render_stickers() {
        function send_sticker_handler(event) {
            let uuid = create_UUID();
            let el = event.target;
            let text = el.dataset.path_128;
            console.warn(el);
            render_message({id: null, text: text, when: Date.now() / 1000, is_sticker: true}, my_user, true, uuid);
            websocket.send(JSON.stringify({action: 'send_message', text: text, uuid: uuid, is_sticker: true}));
            chat_stickers.classList.remove("sticker-show");
        }
        chat_stickers.innerHTML = '';
        for (let {id, path_64, path_128} of data_stickers) {
            let div = document.createElement("div");
            let img = document.createElement("img");
            div.className = "sticker-item";
            img.dataset.id = id;
            img.dataset.path_128 = path_128;
            img.src = path_64;
            div.append(img);
            chat_stickers.append(div);

            img.onclick = send_sticker_handler;
        }
    }

    function action_is_writing(user, users_is_reading) {
        const users_name = users_is_reading.filter(user => user.id !== my_user.id).map(user => user.nickname);
        if (users_name.length > 0) {
            span_is_reading.innerHTML = 'Writing now: ' + JSON.stringify(users_name);
        } else {
            span_is_reading.innerHTML = '';
        }
    }

    function action_delete_messages(id_array) {
        for (let id of id_array) {
            let mes_obj = all_messages.find(mes_obj => mes_obj.id === id);
            if (mes_obj !== undefined) {
                if (selected_edit_message === mes_obj) {
                    selected_edit_message = null;
                    chat_stop_edit_button.classList.remove("to_display_block");
                    text_message.value = '';
                }
                if (selected_messages.length !== 0)
                    removeItemOnce(selected_messages, mes_obj);
                removeItemOnce(all_messages, mes_obj);
                mes_obj.dom_element.remove();
            }

        }
        set_classes_in_header_buttons();
        render_count_messages();
    }

    function action_edit_message(message_id, text) {
        const mes_obj = all_messages.find(mes_obj => mes_obj.id === message_id);
        if (mes_obj !== undefined) {
            mes_obj.text = text;
            mes_obj.dom_element.querySelector(".chat-message-text").innerText = text;
        }

    }

    function init_myuser() {
        const img = chat_header.children[0];
        img.src = '/' + my_user.photopath;
        img.onerror = img_error;
        chat_header.children[1].children[0].innerHTML = my_user.nickname;
    }

    websocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
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
            case 'get_stickers':
                data_stickers = data.stickers;
                break;
            case 'get_one_message':
                if (!is_focus && data.user.id !== my_user.id) {
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
                action_is_writing(data.user, data.users_is_reading);
                break;
            case 'window_onfocus':
                action_onfocus(data.user_id);
                break;
            case 'delete_messages':
                action_delete_messages(data.id_array);
                break;
            case 'edit_message':
                action_edit_message(data.message_id, data.text);
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

    const searchParams = new URLSearchParams(window.location.search);
    websocket.onopen = () => websocket.send(JSON.stringify({
        action: 'init',
        sessionHash: find_cookie("SessionHash"),
        user_id: find_cookie("user_id"),
        chat_id: searchParams.get('chat_id'),
        // password: searchParams.get('pass')
    }));


    const idInterval = setInterval(function () {
        if (is_focus === 1) {
            websocket.send(JSON.stringify({action: 'window_onfocus'}));
        } else {
        }
    }, 2000);


    function initChatEvent() {
        const messageBox = my_form.form_message;
        const button = document.getElementById("form_button");
        let shiftDown = false;
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

        my_form.onsubmit = function (event) {
            event.preventDefault();
            is_reading = false;

            if (selected_edit_message !== null) {
                const text = text_message.value;
                websocket.send(JSON.stringify({action: 'edit_message', text: text, message_id: selected_edit_message.id}));
                websocket.send(JSON.stringify({action: 'reading_message', is_reading: is_reading}));
                selected_edit_message = null;
                text_message.value = '';
                chat_stop_edit_button.classList.remove("to_display_block");
                set_classes_in_header_buttons();
            }
            else {
                let uuid = create_UUID();
                let text = text_message.value;
                if (text.trim() !== '') {
                    render_message({id: null, text: text, when: Date.now() / 1000, is_sticker: false}, my_user, true, uuid);
                    websocket.send(JSON.stringify({action: 'send_message', text: text, uuid: uuid, is_sticker: false}));
                    websocket.send(JSON.stringify({action: 'reading_message', is_reading: is_reading}));
                    text_message.value = '';
                }
            }


            return false;
        };

        function popup_stickers() {
            const button = document.getElementById("form_button_sticker");
            let is_first = true;
            button.onclick = (event) => {
                if (is_first) {
                    is_first = false;
                    render_stickers();
                }
                event.preventDefault();
                chat_stickers.classList.toggle("sticker-show")
            };
        }
        popup_stickers();

        chat_select_delete_button.onclick = (event) => {
            if (selected_messages.length === 0)
                return;
            // for (let mes of selected_messages) {
            //     removeItemOnce(all_messages, mes);
            //     mes.dom_element.remove();
            // }
            const id_array = selected_messages.map((mes) => mes.id);
            websocket.send(JSON.stringify({action: 'delete_messages', id_list: id_array}));
            // selected_messages = [];
            // set_classes_in_header_buttons();
        };

        chat_select_edit_button.onclick = (event) => {
            if (selected_messages.length === 1) {
                selected_edit_message = selected_messages[0];
                selected_edit_message.dom_element.classList.remove("chat_message_select");
                selected_messages = [];
                text_message.value = selected_edit_message.text;
                if (text_message.value.trim() !== '') {
                    websocket.send(JSON.stringify({action: 'reading_message', is_reading: true}));
                }
                chat_stop_edit_button.classList.add("to_display_block");
                set_classes_in_header_buttons();
            }
        };

        chat_stop_edit_button.onclick = (event) => {
            event.preventDefault();
            selected_edit_message = null;
            text_message.value = '';
            websocket.send(JSON.stringify({action: 'reading_message', is_reading: false}));
            chat_stop_edit_button.classList.remove("to_display_block");
        }
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
        });
        return false;
    };

    chat_form_users.querySelector('i').onclick = () => {
        chat_form_users.button.click();
    };

    return {
        close: () => {
            clearInterval(idInterval);
            websocket.close();
        }
    };
}

