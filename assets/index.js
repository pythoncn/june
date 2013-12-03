require('bootstrap');

var $ = require('jquery');
exports.jQuery = $;

$('.comment .delete').on('click', function() {
  var item = $(this);
  var id = item.attr('href').slice(1);
  var url = location.pathname + '/reply?reply=' + id;
  $.ajax({
    url: url,
    method: 'DELETE',
    success: function() {
      item.parentsUntil('.comment').parent().fadeOut();
    }
  });
  return false;
});

$('.comment .reply').on('click', function() {
  var item = $(this);
  var username = item.attr('href').slice(1);
  var form = $('.comment-form textarea');
  var value = form.val();
  value += '@' + username;
  form.val(value);
  form.focus();
  return false;
});

$('.preview-button').on('click', function() {
  var target = $($(this).data('target'));
  var preview = $('#preview-area');

  if (target.hasClass('hide')) {
    target.removeClass('hide');
    preview.hide();
    return false;
  }

  if (!preview.length) {
    preview = $('<div>').attr('id', 'preview-area');
    target.after(preview);
  }
  $.post('/markdown', {content: target.val()}, function(html) {
    preview.html(html);
    preview.show();
    target.addClass('hide');
  });
  return false;
});
