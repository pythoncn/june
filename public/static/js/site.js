(function($){
  // https://gist.github.com/maccman/2907187
  function dragEnter(e) {
    $(e.target).addClass("dragOver");
    e.stopPropagation();
    e.preventDefault();
    return false;
  };
 
  function dragOver(e) {
    e.originalEvent.dataTransfer.dropEffect = "copy";
    e.stopPropagation();
    e.preventDefault();
    return false;
  };
 
  function dragLeave(e) {
    $(e.target).removeClass("dragOver");
    e.stopPropagation();
    e.preventDefault();
    return false;
  };
 
  $.fn.dropArea = function() {
    this.on("dragenter", dragEnter).
         on("dragover",  dragOver).
         on("dragleave", dragLeave);
    return this;
  };

  // https://gist.github.com/maccman/2907189
  var insertAtCaret = function(value) {
    if (document.selection) { // IE
      this.focus();
      sel = document.selection.createRange();
      sel.text = value;
      this.focus();
    } else if (this.selectionStart || this.selectionStart == '0') {
      var startPos  = this.selectionStart;
      var endPos    = this.selectionEnd;
      var scrollTop = this.scrollTop;
 
      this.value = [
        this.value.substring(0, startPos),
        value,
        this.value.substring(endPos, this.value.length)
      ].join('');
 
      this.focus();
      this.selectionStart = startPos + value.length;
      this.selectionEnd = startPos + value.length;
      this.scrollTop = scrollTop;
    } else {
      throw new Error('insertAtCaret not supported');
    }
  };
 
  $.fn.insertAtCaret = function(value){
    $(this).each(function() {
      insertAtCaret.call(this, value);
    })
  };

  function createAttachment(file, dom) {
    var data = new FormData();
    data.append('image', file);

    $.ajax({
      url: '/upload',
      data: data,
      cache: false,
      contentType: false,
      processData: false,
      type: 'POST',
    }).error(function(){
      alert('upload failed');
    }).success(function(data) {
      if (data.error) {
        alert(data.error)
        return;
      }
      var text = '![' + file.name + '](' + data.url + ')';
      dom.insertAtCaret(text)
    });
  };

  $.fn.dropload = function(selector) {
    selector = selector || 'textarea'
    var dom = $(selector);
    if (!dom.length) return;

    $(this).dropArea()
    $(this).on('drop', function(e) {
      e.preventDefault();
      e = e.originalEvent;
      var files = e.dataTransfer.files;
      for (var i=0; i < files.length; i++) {
        // Only upload images
        if (/image/.test(files[i].type)) {
          createAttachment(files[i], dom);
        }
      };
    });
  };
})(jQuery);

(function() {
  // delete a reply
  $('.reply-list .delete').click(function() {
    var self = $(this);
    var replyId = self.attr('href').slice(1);
    $.ajax({
      url: location.pathname + '/reply?reply=' + replyId,
      method: 'DELETE',
      success: function() {
        self.parents('.item').fadeOut();
      }
    });
    return false;
  });

  // preview markdown
  var preview = document.createElement('div');
  $('.preview-button').click(function(e) {
    e.preventDefault();
    var self = $(this);
    var target = $(self.data('target'));
    if (self.hasClass('is-previewing')) {
      // toggle off
      preview.remove();
      target.show();
      self.removeClass('is-previewing');
      return false;
    }
    self.addClass('is-previewing');
    var content = target.val();
    $.post('/markdown', {content: content}, function(data) {
      preview.innerHTML = data;
      target.hide();
      target.after(preview);
    });
    $(preview).on('click', function() {
      preview.remove()
      target.show();
    });
    return false;
  });

  if (/^\/topic\//.test(location.pathname)) {
    $('body').dropload();
  }
})();
