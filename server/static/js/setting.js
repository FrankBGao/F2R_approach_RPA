$(document).ready(function () {

    $(".Detail").click(function () {
        var id_is = this.value;

        $.getJSON("/setting_detail", {id_is: id_is}, function (inputData) {
            $('#one').html(syntaxHighlight(inputData));
        });
    });

});