jQuery.getCookie = function(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
jQuery.sendPost = function(url, args, callback, dataType) {
    if (!dataType) dataType = 'json';
    args._xsrf = $.getCookie('_xsrf');
    if (args._xsrf){
        $.post(url, args, callback, dataType)
        .error(function(jqXHR, textStatus, errorThrown) {
            if (dataType === 'json') {
                callback(jQuery.parseJSON(jqXHR.responseText));
            } else {
                callback(jqXHR.responseText);
            }
        });
    } else {
        var href = '/account/signin?next=' + encodeURI(location.href);
        location.assign(href);
    }
}
jQuery.sendDelete = function(url, args, callback) {
    args._xsrf = $.getCookie('_xsrf');
    if (args._xsrf) {
        url = url + '?' + $.param(args);
        $.ajax({
            url: url,
            dataType: 'json',
            type: 'DELETE',
            success: callback
        }).error(function(jqXHR, textStatus, errorThrown) {
            callback(jQuery.parseJSON(jqXHR.responseText));
        });
    } else {
        var href = '/account/signin?next=' + encodeURI(location.href);
        location.assign(href);
    }
}
