var checkIdIsValid = function(word) {
    return /^[A-Za-z][-A-Za-z0-9_:.]*$/.test(word);
}

$(function() {
    var last = $.cookie('goal-id-open');
    if (last != null && checkIdIsValid(last)) { // if there exists opend accordion item

        // mark all accordion items as closed
        $("#accordion2 .collapse").removeClass('in');

        // show the last opend accordion item
        var idLast = "#" + last;
        var $idLast = $(idLast);
        if ($idLast.length > 0) {
            $idLast.addClass("in");
            $("a.accordion-toggle[href='#" + idLast + "'] > img").css("transform", "rotate(90deg)");
        }
    }

    $('.accordion-toggle').on("click", function() {
        var $this = $(this);
        var bodyId = $(this).attr("href").substr(1);

        // close all accordion items
        $(".accordion-toggle").each(function() {
            var j = $(this).attr('id');
            $("#" + j + " " + "img").css("transform", "rotate(0)");
        });

        if (! $("#" + bodyId).hasClass("in")) { // the accordion item is not opened ?
            // open the accordion item
            $(this).children("img").css("transform", "rotate(90deg)");
            var bodyId = $(this).attr("href").substr(1);
            $.cookie('goal-id-open', bodyId);
        }
    });
});

