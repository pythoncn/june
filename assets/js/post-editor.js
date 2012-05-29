$(function(){
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

    var uploadImage = function(response) {
        var response = $.parseJSON(response);
        if (response.stat == 'fail') {
            alert(response.msg);
            return
        }
        var text = '\n![alt](' + response.url + ')'
        $('#editor textarea').val($('#editor textarea').val() + text).focus();
    }

    var xsrf = '<input name="_xsrf" value="' + $.getCookie('_xsrf') + '" />';
    $('input[type="file"]').uploader({formExtra: xsrf, callback: uploadImage});
});
