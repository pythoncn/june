$(function(){
    var june = window.june || {};
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
    $('.js-follow-node').click(function() {
        var $this = $(this);
        var url = $this.attr('href') + '/follow';
        $.sendPost(url, {}, function(response) {
            if (response.data == 'follow') {
                $this.addClass('following');
                $this.text(june.following);
            } else {
                $this.removeClass('following');
                $this.text(june.follow);
            }
        });
        return false;
    })
    $('.widget-node .following').live({
        mouseenter: function() {
            $(this).text(june.unfollow);
        },
        mouseleave: function() {
            $(this).text(june.following);
        }
    });
});
