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
$('#editor .js-preview').click(function(e) {
    if ($(this).hasClass('active')) return false;
    var text = $('#editor textarea').val();
    if (!text) return false;
    $('#editor .js-write').removeClass('active');
    $('#editor .js-preview').addClass('active');
    $.sendPost('/preview', {'text': text}, function(data){
        $('#editor textarea').hide();
        $('#editor-preview').html(data).show();
    }, 'html');
    return false;
});
$('#editor .js-write').click(function(e) {
    $('#editor .js-preview').removeClass('active');
    $('#editor .js-write').addClass('active');
    $('#editor textarea').show();
    $('#editor-preview').hide();
    return false;
});
