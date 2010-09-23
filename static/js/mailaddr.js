$(document).ready(function() {
    var user = 'petri';
    var host = 'digip.org';
    $('.ma').each(function() {
        var text = $(this).text();
        if($(this).hasClass('s'))
            text = addr = user + '@' + host;
        else
            addr = user + '@' + host;
        $(this).html('<a href="mailto:' + addr + '">' + text + '</a>');
    });
});
