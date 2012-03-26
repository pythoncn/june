/*
 * Copyright (c) 2012 lepture.com
 */

(function($) {
    var uploader = function(options) {
        var settings = {
            'action': '/upload',
            'iframeId': 'uploader-iframe',
            'buttonId': 'uploader-button',
            'buttonText': 'Upload',
            'formExtra': '',
            'callback': null
        }
        if (options) {
            $.extend(settings, options)
        }
        var input = $(this);
        input.after('<a id="' + settings.buttonId + '" href="#">' + settings.buttonText + '</a>');
        var form = document.createElement('form');
        form.method = "post"; form.enctype = "multipart/form-data";
        form.target = 'iframeUploader'; form.action = settings.action;
        $(form).append($(this)).append(settings.formExtra).css({position: 'absolute', left: '-99999px'}).appendTo('body');
        $('#' + settings.buttonId).click(function(){
            input.click();
            return false;
        });
        input.change(function(){
            $('body').append('<iframe id="' + settings.iframeID + '" name="iframeUploader" style="display:none"></iframe>');
            var iframe = $('#' + settings.iframeID).load(function(){
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
