var tab_url;



function getRandomStorageId() {
    var key = Math.floor((Math.random() * 1000000000) + 1);
    if (localStorage.getItem(key)) {
        return Math.floor((Math.random() * 1000000000) + 1);
    }
    return key;
}

chrome.tabs.query({ 'active': true, 'currentWindow': true }, function (tab) {
    tab_url = tab[0].url;
    //refreshSetsList(tab_url);
});

function sendMessage(obj, callback) {
    chrome.tabs.query({ 'active': true, 'currentWindow': true }, function (tab) {
        chrome.tabs.sendMessage(tab[0].id, obj, callback);
    });
}

$(document).ready(function () {
    $("#store").click(function () {
        sendMessage({ "action": 'store' }, function readResponse(obj) {
            var error = $('#error');
            if (!obj || chrome.runtime.lastError || obj.error) {

                if (chrome.runtime.lastError) {
                    error.html('<h6>Error :( Something wrong with current tab. Try to reload it.</h6>');
                } else if (!obj) {
                    error.html('<h6>Error :( Null response from content script</h6>');
                } else if (obj.error) {
                    error.html('<h6>Error :\'( ' + obj.message + '</h6>');
                }

                error.show();
                return;
            } else {
                //error.hide();
                error.html('<h6>Success</h6>');
            }

            var key = getRandomStorageId();

            var setSettings = {
				url: tab_url,
                autoSubmit: false,
                submitQuery: '',
                content: obj.content,
                name: key,
                hotkey: ''
            };

            localStorage.setItem(key, JSON.stringify(setSettings));
        });
    });

});