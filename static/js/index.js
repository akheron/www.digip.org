$(document).ready(function() {
    $('.project').click(function() {
        window.location = $(this).find('a').attr('href');
    });
});
