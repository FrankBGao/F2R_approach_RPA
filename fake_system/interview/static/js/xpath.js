$(document).ready(function () {
    var xpath = "";

    $("*").click(function (e) {
        var inter_xpath = addXpath($(this));
        if (inter_xpath !== false) {
            xpath = inter_xpath + xpath;
        }

    });

    function addXpath($ele) {
        var tagName = $ele[0].tagName.toLowerCase();
        var index = $ele.parent().children(tagName).index($ele) + 1;
        if (tagName !== "html") {
            return '/' + tagName + '[' + index + ']';

        } else {
            return false;
        }
    }

    $('body').on("click keydown", function (item) {
        xpath = "/html[1]" + xpath;

        console.log(xpath);
        xpath = ""
    });

});

