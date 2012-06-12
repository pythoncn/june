/*
 * Copyright (c) 2012 lepture.com
 */

(function($) {
    var uploader = function(options) {
        var settings = {
            'action': '/upload',
            'trigger': '#june-upload-button',
            'formExtra': '',
            'callback': null
        }
        if (options) {
            $.extend(settings, options)
        }
        var input = $(this);
        var form = document.createElement('form');
        form.method = "post"; form.enctype = "multipart/form-data";
        form.target = 'iframeUploader'; form.action = settings.action;

        $(form).append($(this)).append(settings.formExtra).
            css({position: 'absolute', left: '-99999px'}).appendTo('body');

        $(settings.trigger).click(function(){
            input.click();
            return false;
        });
        input.change(function(){
            $('body').append('<iframe id="june-upload-iframe" name="iframeUploader" style="display:none" href="javascript:;"></iframe>');
            var iframe = $('#june-upload-iframe')
            iframe.load(function(){
                var response = iframe.contents().find('body').html();
                if (settings.callback) {
                    settings.callback(response)
                }
                $(iframe).unbind('load');
                iframe.remove();
            });
            form.submit();
        });
    }
    $.fn.uploader = uploader;
})(jQuery);
