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
