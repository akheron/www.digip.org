$(document).ready(function() {
    $('#areas > div').click(function() {
        window.location = $(this).find('a').attr('href');
    });
});
