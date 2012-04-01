/*-------- web font ---------*/
WebFontConfig = {
    google: {families: ['Qwigley']}
};
$('body').append('<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/webfont/1/webfont.js" async=true></script>');
jQuery.getCookie = function(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
jQuery.sendPost = function(url, args, callback, dataType) {
    args._xsrf = $.getCookie('_xsrf');
    if (args._xsrf){
        $.post(url, args, callback, dataType)
    }
    else {
        var href = '/account/signin?next=' + encodeURI(location.href);
        location.assign(href);
    }
}
$("a[href*='http://']:not([href*='"+location.hostname+"'])").attr("target","_blank");
$('a[title]').tipsy({gravity: $.fn.tipsy.autoNS});
$('time.updated').timeago();
$('#nav-toggle').click(function(e){$('body').toggleClass('expanded'); return false;});
$('#notify .js-hide').click(function(e) {
    $(this).parentsUntil($('#notify'), '.message').remove();
});
$('.topics time.updated').each(function(i, item) {
    var dis = (new Date()).getTime() - $.timeago.parse($(item).attr('datetime')).getTime();
    if (dis < 600000) {
        $(item).parentsUntil($('.topics'), 'li').addClass('new');
    }
});
/*------ footer --------*/
if($(window).height() >= $(document).height())$('#footer').addClass('show');
$(window).scroll(function(){
    var wh = $(window).height();
    var dh = $(document).height();
    var fh = $('#footer').height();
    var s = $('body').scrollTop();
    if ((s + wh + fh) > dh) {
        $('#footer').addClass('show');
    } else {
        $('#footer').removeClass('show');
    }
});
/*------ editor -------*/
$('#editor .js-preview').click(function(e) {
    if ($(this).hasClass('current')) return false;
    var text = $('form textarea').val();
    if (!text) return false;
    $('#editor .js-write').removeClass('current');
    $('#editor .js-preview').addClass('current');
    $.sendPost('/preview', {'text': text}, function(data){
        $('form textarea').hide();
        $('#editor-preview').html(data).show();
    }, 'html');
    return false;
});
$('#editor .js-write').click(function(e) {
    $('#editor .js-preview').removeClass('current');
    $('#editor .js-write').addClass('current');
    $('form textarea').show();
    $('#editor-preview').hide();
    return false;
});
/*-------- vote -------*/
$('.vote .ui-btn').click(function(){
    var that = $(this);
    var url = '/api/' + that.attr('data-api');
    if (url.indexOf('down') == -1) {
        var type = 'like';
    } else {
        var type = 'hate';
    }
    $.sendPost(url, {}, function(data){
        if (data.status == 'fail') {
            alert(data.msg);
        } else {
            that.toggleClass('active');
            that.text(data.data.count + ' ' + type);
        }
    }, 'json');
    return false;
});

if(user.username) {
    var topic_owner = $('#main article.hentry div.vcard a.fn').text();
    if (topic_owner && user.username == topic_owner) {
        $('ol.replies li').hover(function(e){
            var that = $(this);
            if (that.hasClass('accepted')) {
                that.find('div.meta').append('<a class="btn" href="#">Cancel</a>');
            } else {
                that.find('div.meta').append('<a class="btn" href="#">Accept</a>');
            }
            $('ol.replies li a.btn').click(function(e) {
                var url = '/api/topic/' + $('article.hentry').attr('data-id') + '/' + that.attr('data-id') + '/accept';
                $.sendPost(url, {}, function(data){
                    if (data.status == 'fail') {
                        alert(data.msg);
                    } else {
                        that.toggleClass('accepted');
                    }
                }, 'json');
                return false;
            });
        }, function(e){
            var that = $(this);
            that.find('a.btn').remove();
        });
    }
}
/* ------- alert ---------*/
$('.js-confirm').click(function(e) {
    return confirm("Are you sure?");
});
