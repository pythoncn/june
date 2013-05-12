(function() {

  // delete a reply
  $('.reply-list .delete').click(function() {
    var self = $(this);
    var replyId = self.attr('href').slice(1);
    $.ajax({
      url: location.pathname + '/reply',
      method: 'DELETE',
      success: function() {
        self.parents('.item').fadeOut();
      }
    });
    return false;
  });

})();
