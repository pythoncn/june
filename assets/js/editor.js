$(function(){
    var cache = {
        set: function(key, value) {
            if (localStorage) {
                localStorage[key] = value;
            }
        },
        get: function(key) {
            if (localStorage) {
                return localStorage[key];
            }
            return '';
        }
    }
    $('#markdown-syntax .js-toggle').click(function(){
        var icon = $(this).find('span');
        if (icon.hasClass('icon-up-open')) {
            icon.attr('class', 'icon-down-open');
            $('#markdown-syntax .ui-box-container').slideUp();
            cache.set('markdown-syntax', '');
        } else {
            icon.attr('class', 'icon-up-open');
            $('#markdown-syntax .ui-box-container').slideDown();
            cache.set('markdown-syntax', 'expand');
        }
        return false;
    });
    if (cache.get('markdown-syntax') === 'expand') {
        $('#markdown-syntax .js-toggle span').attr('class', 'icon-up-open');
        $('#markdown-syntax .ui-box-container').removeClass('fn-hide');
    }

    marked.setOptions({
        gfm: true,
        pedantic: false,
        sanitize: true
    });
    var $textarea = $('#editor textarea');
    var $preview = $('#markdown-preview-container');
    var height = $textarea.height();
    if ($textarea.val()) {
        $preview.html(marked.parse($textarea.val()));
    } else {
        var text = cache.get(location.pathname);
        $textarea.val(text);
        if (text) $preview.html(marked.parse(text));
    }
    $textarea.keyup(function(){
        $preview.html(marked.parse($textarea.val()));
        $textarea.height(Math.max($preview.height(), height));
        cache.set(location.pathname, $textarea.val());
    });
});
