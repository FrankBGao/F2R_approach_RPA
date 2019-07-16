$(document).ready(function () {
    mermaid.initialize({
        theme: 'default'
    });
    $(".Detail").click(function () {
        var response = document.querySelector("#flow_chart");
        var condition = $("#condition");
        var condition_pic = $("#condition_pic");
        var id_is = this.value;

        $.getJSON("/rule_detail", {id_is: id_is}, function (inputData) {
            response.innerHTML = "";
            var insertSvg = function (svgCode, bindFunctions) {
                response.innerHTML = svgCode;
            };

            var graphDefinition = inputData["response"];
            mermaid.render('graphDiv', graphDefinition, insertSvg);

            if (inputData["condition_type"] === "modeled") {
                condition.show();
                condition_pic.hide();
                condition.html(inputData["condition"])
            } else {
                condition.hide();
                condition_pic.show();
                condition_pic.attr('src', "data:image/png;base64," + inputData["condition"]);
            }

        });
    });

    $(".Delete").click(function () {
        var id_is = this.value;
        $.get("/delete_rule", {id_is: id_is}, function (returned) {
            if(returned==="success"){
                $("#"+id_is).hide();
            }
        });
    });
});