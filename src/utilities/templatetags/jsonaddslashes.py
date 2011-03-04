from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def jsonaddslashes(value):
    """
    For use in JSON objects.

    For instance, like this:
    { "key: "{% filter addslashes %}value{% endfilter %}" }

    - Double quotes should be escaped.
    - Single quotes shouldn't be escaped. (Not valid.)
    - Tabs should be escaped.
    - Newline/CR characters should be replaced by their escape character.
    - JSON strings are always put in double quotes.
    """

    return mark_safe(value \
            .replace("\\", r"\\") \
            .replace('"', r'\"') \
            .replace("'", r"'") \
            .replace("\n", r"\n") \
            .replace("\r", r"\r") \
            .replace("\t", r"\t"))

jsonaddslashes.is_safe = True
