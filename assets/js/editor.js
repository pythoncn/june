var converter = new Showdown.converter()
var textarea = $('#editor textarea');
if (textarea.val()) {
    var txt = textarea.val().replace('<', '&lt;').replace('>', '&gt;');
    var html = converter.makeHtml(txt);
    $('#markdown-preview').html(html);
}
textarea.keyup(function(){
    var txt = $(this).val().replace('<', '&lt;').replace('>', '&gt;');
    var html = converter.makeHtml(txt);
    $('#markdown-preview').html(html);
});
$('body').addClass('expanded');
