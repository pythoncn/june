$(function(){
    $("a[href*='http://']:not([href*='"+location.hostname+"'])").attr("target","_blank");
    $('a[title]').tipsy({gravity: $.fn.tipsy.autoNS});

    $('.js-overlay').click(function(){
        $('body').addClass('overlay-mode');
        return false;
    });
    $('.ui-overlay,.js-close-overlay').click(function() {
        $('body').removeClass('overlay-mode');
        return false;
    });
});
