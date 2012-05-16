$(function(){
    marked.setOptions({
        gfm: true,
        pedantic: false,
        sanitize: true
    });
    var $textarea = $('#editor textarea');
    var $preview = $('#markdown-preview-container');
    $preview.html(marked.parse($textarea.val()));
    $textarea.keyup(function(){
        $preview.html(marked.parse($textarea.val()));
    });
});
