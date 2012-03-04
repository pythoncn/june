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
$('#notify .j-hide').click(function(e) {
    var notify = $(this).attr('data-notify');
    console.log(notify);
    var p = $(this).parentsUntil($('#notify'), '.message').remove();
});
$('div.up-vote, div.down-vote').click(function(e){
    var that = $(this);
    var url = that.attr('data-url');
    if (!url) return;
    $.sendPost(url, {}, function(data){
        if(data == "1") that.toggleClass('active');
    }, 'html');
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
