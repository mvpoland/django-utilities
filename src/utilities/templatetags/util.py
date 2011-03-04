from django.template import Node, Variable, defaultfilters
from django import template
from django.utils.translation import ugettext as _
from django.template.defaultfilters import safe, date

import random
import math
import decimal
import datetime

register = template.Library()

@register.filter
def month_name(month_number, format):
    try:
        month_number = int(month_number)
    except ValueError:
        return ''
    if month_number > 12 or month_number < 1:
        return ''

    today = datetime.date.today()
    today = today.replace(day=1, month=month_number)

    return date(today, format)

@register.filter
def split_amount(value):
    if value:
        splitted = value.split('.') if '.' in value else value.split(',')
        if len(splitted) == 1:
            splitted.append('00')
        return "%s<span class=\"decimals\">,%s</span>" % (splitted[0], splitted[1])
    else:
        return value
split_amount.is_safe=True

def split_data(value):
    if value:
        splitted = value.split(' ')
        return "%s&nbsp;<span class=\"data\">%s</span>" % (splitted[0], splitted[1])
    else:
        return value
split_data.is_safe=True
register.filter("split_data", split_data)


@register.filter
def empty(value, default=""):
    if not value:
        if not default:
            default = _("empty")
        value = "%s%s%s" % ('<span class="lighter smaller">', default, "</span>")
    return safe("%s" % (value,))
empty.is_safe=True

def math_absolute(value):
    return math.fabs(value)
register.filter("absolute", math_absolute)

@register.filter
def replace(value, arg):
    splitted = arg.split('|')

    return value.replace(splitted[0], splitted[1])

@register.filter
def multiply(value, arg):
    return decimal.Decimal(value) * decimal.Decimal(arg)

@register.filter
def divide(value, arg):
    return decimal.Decimal(value) / decimal.Decimal(arg)


class MoreLessNode(Node):
    def __init__(self, text):
        self.text = Variable(text)

    def render(self, context):
        text = self.text.resolve(context)
        text = defaultfilters.urlize(text)

        random_id = random.randint(0,1000000000)

        value = '<div id="description_%s"><div class="info_less"><p>%s ' % (random_id, defaultfilters.truncatewords_html(text, 25),)
        if defaultfilters.wordcount(text) > 25:
            value += ' <a id="link_more_%s" class="bold small link_more" href="">%s</a>' % (random_id, _("show more"),)
        value += '</p></div>'
        value += '<div class="info_more" style="display:none;">%s <p><a id="link_less_%s" class="bold small link_less" href="">%s</a></p></div></div>' % (defaultfilters.linebreaks(text), random_id,_("show less"))

        return value


@register.tag
def more_less(parser, token):
    args = token.split_contents()

    if len(args) == 2:
        return MoreLessNode(args[1])
    else:
        raise TemplateSyntaxError, "%r tag expects 2 arguments (got %s)" % (args[0], len(args))


@register.filter
def prettify_phonenumber(value):
    from cl_utils.utils import check_cell_phone_number
    number = check_cell_phone_number(unicode(value))
    if number is not None:
        values = {'country': number[0:3],
                  'area': number[3:6],
                  'r1': number[6:12],
                  'r2_1': number[6:8],
                  'r2_2': number[8:10],
                  'r2_3': number[10:12],
                  'r3_1': number[6:9],
                  'r3_2': number[9:12],}
        #return u'%(country)s %(area)s %(r3_1)s %(r3_2)s' % values
        return u'%(country)s %(area)s %(r2_1)s %(r2_2)s %(r2_3)s' % values
    else:
        return value

@register.filter
def prettify_trackingnumber(value):
    if not value.isdigit():
        return value

    r_value = value[::-1]
    prettified = u''

    for id,character in enumerate(r_value):
        if id % 3 == 0:
            prettified = ' ' + prettified
        prettified = character + prettified

    return prettified

@register.filter
def external_urlize(value, autoescape=None):
    from django.template.defaultfilters import urlize

    value = urlize(value, autoescape)
    value = value.replace("a href", 'a rel="external" href')

    return safe(value)
external_urlize.is_safe=True
external_urlize.needs_autoescape = True


# =========== removehtml, a patch to striptags which also decodes the entities ===

from django.template.defaultfilters import stringfilter

@register.filter
@stringfilter
def removehtml(value):
    """
    Strips all HTML tags and replaces the remaining entities
    by their original character.

    input example. "U.S. Adviser&#8217;s Blunt Memo on Iraq: Time &#8216;to Go Home&#8217;"

    See also:
    /python2.6/site-packages/django/template/defaultfilters.py
    http://stackoverflow.com/questions/1208916/decoding-html-entities-with-python
    """
    from django.utils.html import strip_entities, strip_tags
    value = strip_tags(value)


    # Strip entities
    from BeautifulSoup import BeautifulStoneSoup
    return BeautifulStoneSoup(value, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)

removehtml.is_safe = True

@register.filter
def filesizeformat(bytes):
    """
    Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, 2047.4 MB, 2.0 GB, etc).
    """
    try:
        bytes = float(bytes)
    except (TypeError,ValueError,UnicodeDecodeError):
        bytes = 0

    if bytes == 1:
        return _("%(size)d byte") % {'size': bytes}

    if bytes < 1024:
        return _("%(size)d bytes") % {'size': bytes}
    if bytes < 1024 * 1024:
        return _("%.1f KB") % (bytes / 1024)
    # only show GB if it's on the GB or >= 10GB
    if bytes % (1024**3) == 0 or bytes > 10*1024**3:
        return _("%.1f GB") % (bytes / (1024 * 1024 * 1024))
    return _("%.1f MB") % (bytes / (1024 * 1024))
filesizeformat.is_safe = True


@register.filter
def classname(value):
    return safe(value.__class__.__name__)
classname.is_safe = True

