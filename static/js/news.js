var step = 5;

function show_news(count) {
    // Make count a multiple of step
    count = count + ((step - (count % step)) % step);

    $('#news tr:lt(' + count + ')').show();
    $('#news tr:gt(' + (count - 1) + ')').hide();

    if($('#news tr:hidden').length == 0) {
        $('#morenews').hide();
    } else {
        $('#morenews').show();
    }

    if($('#news tr:visible').length == step) {
        $('#lessnews').hide();
    } else {
        $('#lessnews').show();
    }
}

function init_news() {
    $('#news').after(
            '<p>' +
            '<a id="morenews" href="javascript:;">(Show more news)</a> ' +
            '<a id="lessnews" href="javascript:;">(Show less news)</a>' +
            '</p>');
    $('#morenews').click(
        function() {
            show_news($('#news tr:visible').length + step);
        });
    $('#lessnews').click(
        function() {
            show_news($('#news tr:visible').length - step);
        });
}

$(document).ready(
    function() {
        init_news();
        show_news(step);
    }
);
