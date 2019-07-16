$(document).ready(function () {
    $("#button_page_rule").click(function () {window.location.replace("/show_rules");});
    $("#button_page_form_setting").click(function () {window.location.replace("/show_form_setting");});
    $("#button_page_commander").click(function () {window.location.replace("/show_commander");});
    $("#button_page_io_log").click(function () {window.location.replace("/show_iolog");});
});

// thanks this page https://www.jianshu.com/p/04127d74d88c, for the syntaxHighlight
function syntaxHighlight(json) {
    if (typeof json !== 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}