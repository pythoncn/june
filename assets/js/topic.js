$(function(){
    $.sendPost(location.pathname);
    $('.js-up-vote').click(function(){
        var url = location.pathname + '/vote'
        var $this = $(this);
        $.sendPost(url, {action: 'up'}, function(data) {
            if (data.stat == 'ok') {
                $this.toggleClass('active');
                $this.find('.count').text(data.data);
            } else {
                alert(data.msg);
            }
        });
        return false;
    });
    $('.js-down-vote').click(function(){
        var url = location.pathname + '/vote'
        var $this = $(this);
        $.sendPost(url, {action: 'down'}, function(data) {
            if (data.stat == 'ok') {
                $this.toggleClass('active');
                $this.find('.count').text(data.data);
            } else {
                alert(data.msg);
            }
        });
        return false;
    });
    $('.js-accept').click(function(){
        var url = '/reply/' + $(this).attr('href').slice(1);
        var $this = $(this);
        $.sendPost(url, {}, function(data) {
            if (data.stat === 'ok') {
                $this.parents('.ui-cell-bottom-right').toggleClass('active');
            } else {
                alert(data.msg);
            }
        });
        return false;
    });
    $('.js-delete').click(function(){
        var url = '/reply/' + $(this).attr('href').slice(1);
        var $this = $(this);
        $.sendDelete(url, {}, function(data) {
            if (data.stat === 'ok') {
                $this.parents('.ui-cell').remove();
            } else {
                alert(data.msg);
            }
        });
        return false;
    });
    var names = [$('.username strong').text()];
    $('.reply-meta>a').each(function(i, o){
        var name = $(o).text();
        if (names.indexOf(name) == -1) names.push(name);
    });

    $('#editor textarea').atWho('@', {data: names});
});
