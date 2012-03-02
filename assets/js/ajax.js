// {{{ pannel behavior
var _href = location.href;
$('div.js-snippet').click(function(e){
    if (e.target.tagName == 'a') return;
    var url = $(this).attr('data-url');
    if (!url) return;
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
$('#overlay').click(function(e) {
    $(this).hide();
    $('#pannel').css('right', -650);
    !!history.pushState && history.pushState(null, '', _href);
});
// }}}
// {{{ form behavior
$('form.js-form').submit(function(e) {
    var data = $(this).serialize();
    var url = $(this).attr('action');
    console.log(data);
    $.post(url, data, function(data) {
        console.log(data);
    });
    return false;
});
// }}}
