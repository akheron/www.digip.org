$(document).ready(function() {
    var host = "digip.org";
    $('.mailaddr').each(function() {
        var text = $(this).text();
        var bar = text.indexOf('|');
        var addr, display;
        if(bar != -1) {
          display = text.slice(0, bar);
          addr = text.slice(bar + 1) + '@' + host;
        }
        else {
          addr = text + '@' + host;
          display = addr;
        }
        $(this).html('<a href="mailto:' + addr + '">' + display + '</a>');
      });
  });
