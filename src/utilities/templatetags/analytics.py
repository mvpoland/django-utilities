from django import template
from django.conf import settings

register = template.Library()

def make_tracker_code(urchin_id, tracker_code):
    if urchin_id is None:
        urchin_id = getattr(settings, 'URCHIN_ID', None)
    if urchin_id is not None:
        return tracker_code % urchin_id
    else:
        return ''

@register.simple_tag
def urchin(urchin_id=None):
    return make_tracker_code(urchin_id, '''
    <script src="http://www.google-analytics.com/urchin.js" type="text/javascript"></script>
    <script type="text/javascript">
    //<![CDATA[
        try {
            _uacct = "%s";
            urchinTracker();
        } catch(err) {}
    //]]>
    </script>
    ''')

@register.simple_tag
def google_analytics(urchin_id=None):
    return make_tracker_code(urchin_id, '''
    <script type="text/javascript">
    //<![CDATA[
        var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
        document.write(unescape("%%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%%3E%%3C/script%%3E"));
    //]]>
    </script>
    <script type="text/javascript">
    //<![CDATA[
        try {
            var pageTracker = _gat._getTracker("%s");
            pageTracker._trackPageview();
        } catch(err) {}
    //]]>
    </script>
    ''')

@register.simple_tag
def google_analytics_async(urchin_id=None):
    return make_tracker_code(urchin_id, '''
    <script type="text/javascript">
    //<![CDATA[
        var _gaq = _gaq || [];
        _gaq.push(['_setAccount', '%s']);
        _gaq.push(['_trackPageview']);

        (function() {
            var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
            ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(ga);
        })();
    //]]>
    </script>
    ''')
