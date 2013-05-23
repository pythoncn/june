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
})();
