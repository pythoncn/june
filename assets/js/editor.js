$(function(){
    marked.setOptions({
        gfm: true,
        pedantic: false,
        sanitize: true
    });
    var $textarea = $('#editor textarea');
    var $preview = $('#markdown-preview-container');
    if ($textarea.val()) {
        $preview.html(marked.parse($textarea.val()));
    };
    $textarea.keyup(function(){
        $preview.html(marked.parse($textarea.val()));
    });
});
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
