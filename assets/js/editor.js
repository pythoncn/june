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

var uploadImage = function(response) {
    var response = $.parseJSON(response);
    if (response.stat == 'fail') {
        alert(response.msg);
        return
    }
    var text = '\n![alt](' + response.url + ')'
    textarea.val($('#editor textarea').val() + text).focus();
}

var xsrf = '<input name="_xsrf" value="' + $.getCookie('_xsrf') + '" />';
$('input[type="file"]').uploader({formExtra: xsrf, callback: uploadImage});
$('body').addClass('expanded');
