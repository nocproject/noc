function toggle_password(element_id, show_text) {
    if(document.getElementById) {
        var password_input = document.getElementById(element_id);
        var new_input      = document.createElement('input');
        with(new_input) {
            id        = password_input.id;
            name      = password_input.name;
            value     = password_input.value;
            size      = password_input.size;
            className = password_input.className;
            type      = show_text ? 'text' : 'password';
        }
    password_input.parentNode.replaceChild(new_input,password_input);
    }
}
