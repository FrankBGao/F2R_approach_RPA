var url = "http://127.0.0.1:8000/";

function getElementByXpath(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

// xpath
function addXpath($ele) {
    var tagName = $ele[0].tagName.toLowerCase();
    var index = $ele.parent().children(tagName).index($ele) + 1;
    if (tagName !== "html") {
        return '/' + tagName + '[' + index + ']';

    } else {
        return false;
    }
}


$(document).ready(function () {
    var reg=/(^[\-0-9][0-9]*(.[0-9]+)?)$/;
    var pattern=new RegExp(reg);

    var current_url = $(location).attr('href');
    var setting = "";

    $.ajaxSettings.async = false;
    $.getJSON(url + "form_setting", {url: current_url}, function (inputData) {
        setting = inputData;
    });
    $.ajaxSettings.async = true;

    if (setting["NotAllow"]) {
        return;
    }
    // xpath
    var xpath = "";

    $("*").click(function (e) {
        if (setting["NotAllow"]) {
            return;
        }

        var inter_xpath = addXpath($(this));
        if (inter_xpath !== false) {
            xpath = inter_xpath + xpath;
        }

    });

    var filed = setting["form_field"];
    var fread = {};
    var fwrite = {};

    filed.forEach(function (v) {
        var inter = getElementByXpath(v["address"]);
        if(pattern.test(inter.value)){
            fread[v["name"]] = parseFloat(inter.value);
        }else {
            fread[v["name"]] = inter.value;
        }
    });
    var tb = Date.parse(new Date());

    var fa = {
        fread: fread,
        fwrite: fwrite,
        tb: tb,
        tf: "",
        u: "resource",
        frm: setting["name"],
        fa_id: setting["fa_id"]
    };
    
    var post = {"data":JSON.stringify(fa)};
    $.post(url+ "receive_form_action",post);

    $('body').on("click keydown", function (item) {
        if (setting["NotAllow"]) {
            xpath = "";
            return;
        }

        var typeIs = item.handleObj.type; // keydown, click
        if (typeIs === "keydown") {
            typeIs = item.originalEvent.code;
        }

        xpath = "/html[1]" + xpath;
        if ((setting["finish_route"]["address"] !== xpath) || (setting["finish_route"]["motion"] !== typeIs)) {
            xpath = "";
            return;
        }
        filed.forEach(function (v) {
            var inter = getElementByXpath(v["address"]);

            if(pattern.test(inter.value)){
                fwrite[v["name"]] = parseFloat(inter.value);
            }else {
                fwrite[v["name"]] = inter.value;
            }
        });
        var tf = Date.parse(new Date());
        fa["fwrite"] = fwrite;
        fa["tf"] = tf;

        var post = {"data":JSON.stringify(fa)};
        $.post(url+ "receive_form_action",post);
        xpath = ""
    });
});

