var amount = 5;

function hide_news() {
    $('#news tr:gt(' + (amount - 1) + ')').hide();
    if($('#news tr:hidden').length) {
        $('#news').after('<p><a id="morenews" href="javascript:;">(Show more news)</a></p>');
        $('#morenews').click(
            function() {
                $('#news tr:hidden:lt(' + amount + ')').show();
                if(!$('#news tr:hidden').length) {
                    $('#morenews').hide();
                }
            }
        );
    }
}

$(document).ready(hide_news);
