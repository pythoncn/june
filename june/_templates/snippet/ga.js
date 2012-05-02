{% if g.ga %}
    var _gaq = _gaq || [];
_gaq.push(['_setAccount', '{{g.ga}}']);
_gaq.push(['_trackPageview']);
_gaq.push(['_trackPageLoadTime']);
_gaq.push(['_setCustomVar', 1, 'UserType', {%if current_user%}'Member'{%else%}'Guest'{%end%}, 2]);
(function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
{% end %}
