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

$('.like-topic').on('click', function() {
  var item = $(this);
  var url = location.pathname + '/like';
  item.find('.glyphicon').toggleClass('glyphicon-heart').toggleClass('glyphicon-heart-empty');
  $.ajax({
    url: url,
    method: 'POST',
    success: function(data) {
      if (data.action === 'cancel') {
        item.find('.glyphicon').removeClass('glyphicon-heart').addClass('glyphicon-heart-empty');
      } else {
        item.find('.glyphicon').removeClass('glyphicon-heart-empty').addClass('glyphicon-heart');
      }
    }
  });
  return false;
});
