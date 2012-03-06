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
$('time.updated').timeago();
_gaq = window._gaq || [];
// {{{ pannel behavior
var _href = location.href;
$('div.js-snippet').click(function(e){
    if(e.target.tagName.toLowerCase() == 'a') return;
    var url = $(this).attr('data-url');
    if (!url) return;
    if (!$('#pannel').length) {
        $('body').append('<div id="pannel"></div><div id="overlay"></div>');
        $('#overlay').click(function(e) {
            $(this).hide();
            $('#pannel').css('right', -670);
            !!history.pushState && history.pushState(null, '', _href);
        });
    }
    !!history.pushState && history.pushState(null, '', url);
    $('#pannel > div[data-snippet]').hide();
    var snippet = $('#pannel > div[data-snippet="' + url + '"]');
    if (snippet.length) {
        $('#overlay').show();
        snippet.show();
        $('#pannel').css('right', 0);
        return;
    }
    $.get(url, function(data) {
        $('#overlay').show();
        var html = '<div data-snippet="' + url + '">' + data + '</div>';
        $('#pannel').append(html).css('right', 0);
    });
});
// }}}
$('#notify .js-hide').click(function(e) {
    var notify = $(this).attr('data-notify');
    console.log(notify);
    var p = $(this).parentsUntil($('#notify'), '.message').remove();
});
$('div.vote div[data-url]').click(function(){
    var that = $(this);
    var url = that.attr('data-url');
    $.sendPost(url, {}, function(data){
        if (data.status == 'ok') {
            that.toggleClass('active');
            _gaq.push(['_trackEvent', 'vote', data.msg, url]);
        } else {
            alert(data.msg);
            _gaq.push(['_trackEvent', 'vote', 'fail', url]);
        }
    }, 'json');
});
$('a.js-follow').click(function(e) {
    _gaq.push(['_trackEvent', 'follow', 'follow', $(this).attr('url')]);
});
$('a.js-unfollow').click(function(e) {
    _gaq.push(['_trackEvent', 'follow', 'unfollow', $(this).attr('url')]);
});
$('a.js-preview').click(function(e) {
    if (!$('#pannel').length) {
        $('body').append('<div id="pannel"></div><div id="overlay"></div>');
        $('#overlay').click(function(e) {
            $(this).hide();
            $('#pannel').css('right', -670);
        });
    }
    $.sendPost('/preview', {'text': $('form textarea').val()}, function(data){
        $('#overlay').show();
        var html = '<div class="wrapper">' + data + '</div>';
        $('#pannel').html(html).css('right', 0);
    }, 'html');
    return false;
});
// {{{ form behavior
/*
$('form.js-form').submit(function(e) {
    var data = $(this).serialize();
    var url = $(this).attr('action');
    console.log(data);
    $.post(url, data, function(data) {
        console.log(data);
    });
    return false;
});
*/
// }}}
