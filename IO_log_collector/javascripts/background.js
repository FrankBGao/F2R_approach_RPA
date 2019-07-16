function getHotkeys(url) {
    var sets = getSetsForCurrentUrl(url);
    var hotkeys = [];

    for (var i = 0; i < sets.length; i++) {
        if (!sets[i].hotkey) {
            continue;
        }

        hotkeys.push(sets[i].hotkey);
    }

    return hotkeys;
}

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    var hotkeys = getHotkeys(request.url);

    switch (request.action) {
        case 'gethotkeys':
            sendResponse(hotkeys);
            break;

        case 'hotkey':
            var sets = getSetsForCurrentUrl(request.url);
            for (var i = 0; i < sets.length; i++) {
                if (sets[i].hotkey == request.code) {
                    sendResponse(sets[i]);
                }
            }
            break;
    }

    return true;
});

/////////////////////////////////////////////
var g_content;
var g_timestamp;
var url_post = "http://127.0.0.1:8000/receive_request";

// function getRandomStorageId() {
//     var key = Math.floor((Math.random() * 1000000000) + 1);
//     if (localStorage.getItem(key)) {
//         return Math.floor((Math.random() * 1000000000) + 1);
//     }
//     return key;
// }

function readResponse(obj) {
    var timestamp = Date.parse(new Date());

    if(obj === undefined || obj.content === "{}"){
        return;
    }

    if(g_content === obj.content && g_timestamp === timestamp){
        return;
    }

    if(obj.content.indexOf("? undefined:undefined ?") !== -1){
        return;
    }

    //var key = getRandomStorageId();
    //var inter_timestamp = new Date().getTime();
    var setSettings = {
        content: obj.content,
        timestamp: timestamp,
        resource:"Resource",
        requestDetail: obj.requestDetail
    };
    $.post(url_post,setSettings);
    g_timestamp = timestamp;
    g_content = obj.content;
    //localStorage.setItem(key, JSON.stringify(setSettings));
}


function sendMessage(detail) {
    // filter some request which is not form
    //console.log(detail);
    if (
        detail.url !== url_post && // post to info receiver
        detail.url.indexOf("cuscochromeextension")===-1 && // some Chrome extension request
        detail.url.indexOf(".css")===-1 &&
        detail.url.indexOf(".js")===-1 &&
        detail.type !== "image"
    ){
        chrome.tabs.query({'active': true, 'currentWindow': true}, function (tab) {

            if( tab.length > 0 && // have tab
                (tab[0]['url'].indexOf(detail["initiator"]) !== -1 || // get ride of the Request not from this tab
                    tab[0]['url'] === detail["url"])
            ){
                var info = {
                    request:detail,
                    tab_title: tab[0]['title'],
                    tab_url: tab[0]['url'],
                };
                chrome.tabs.sendMessage(tab[0].id, info, readResponse); // send message to content_scipt
            }
        });

    }
    return(detail);
}

function GainResponse(detail) {
    return(detail);
}
function HeadersReceived(detail) {
    return(detail);
}
var filters = {urls: ["<all_urls>"]};
var opt_extraInfoSpec = ["requestBody"]; //"requestBody"

// listen the request from brower
chrome.webRequest.onBeforeRequest.addListener(sendMessage, filters, opt_extraInfoSpec);



// listen the Response from brower
// chrome.webRequest.onResponseStarted.addListener(GainResponse, filters);
// chrome.webRequest.onHeadersReceived.addListener(HeadersReceived, filters);

// chrome.devtools.network.onRequestFinished.addListener(function(request) {
//         var content = getContent(request);
//         console.log(content);
// });

// chrome.webRequest.onSendHeaders.addListener(function (e) {
//     console.log(e);
// },filters,["requestHeaders"]);
